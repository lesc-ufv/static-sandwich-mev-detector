from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import HighLevelCall, LowLevelCall, InternalCall, Binary, BinaryType, SolidityCall, LibraryCall
from slither.core.cfg.node import NodeType
from slither.analyses.data_dependency.data_dependency import is_dependent
from slither.core.solidity_types import ElementaryType

class StaticSandwichDetector(AbstractDetector):
    """
    Static MEV Sandwich Detector.
    
    1. Finds 'Active' Data Sources:
       - Output of CALL/DELEGATECALL (Swaps).
       - Output of 'balanceOf' (Balance Checks).
       - Explicitly IGNORES 'STATICCALL'.
    
    2. Finds 'Slippage' Sinks:
       - Inequality comparisons (<, >, <=, >=).
       - Explicitly IGNORES Equality checks (==, !=).
       
    3. Connects them via Data Dependency.
    """
    
    ARGUMENT = 'static-sandwich'
    HELP = 'Detects slippage checks via structural inequality analysis'
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = (
        "https://github.com/lesc-ufv/static-sandwich-mev-detector"
    )

    WIKI_TITLE = "MEV Sandwich Opportunity Detector"

    # region wiki_description
    WIKI_DESCRIPTION = """
    **MEV Sandwich Opportunity Detector**

    This detector identifies smart contract logic susceptible to MEV Sandwich by analyzing the data flow of trade execution. It flags structural patterns where a state-dependent value (Active Source)—such as the return value of a swap or a post-execution balance update—is validated against a user-supplied parameter (User Input) using an inequality check.

    In a MEV Sandwich, an adversary observes a victim's pending transaction with high slippage tolerance. The attacker exploits this by front-running the victim (buying the asset to inflate the price) and then back-running the execution (selling for a profit). This opportunity manifests in code when the mechanism to enforce the "minimum acceptable amount" is absent, optional, or structurally decoupled from the actual output of the external call.
    """
    # endregion wiki_description

    # region wiki_exploit_scenario
    WIKI_EXPLOIT_SCENARIO = """
    **Scenario: The MEV Sandwich**
    A user initiates a transaction to swap 1000 USDC for ETH via a vulnerable router, setting a `minAmountOut` of 0 or a value significantly below the market rate (high slippage tolerance).

    1.  **Front-run:** An MEV bot detects the pending transaction in the mempool. It pays a higher gas fee to execute a large buy order for ETH immediately *before* the user's transaction, artificially driving up the price of ETH in the liquidity pool.
    2.  **Victim Execution:** The user's transaction executes at this inflated price. The router contract checks `amountReceived >= minAmountOut`. Since `minAmountOut` is low, the check passes, but the user receives significantly less ETH than anticipated.
    3.  **Back-run:** The bot immediately sells the ETH it bought in step 1. Because the victim's trade pushed the price even higher, the bot profits from the price difference, extracting value directly from the victim's trade execution.
    """
    # endregion wiki_exploit_scenario

    WIKI_RECOMMENDATION = """
    **Remediation Guidelines:**

    1.  **Mandatory Slippage Protection:** Ensure all swap functions accept and enforce a user-defined `amountOutMin` parameter. Avoid hardcoding slippage values or defaulting them to zero.
    2.  **Verify Execution Outputs:** Validate the *actual* output of the swap against the minimum requirement. This must be done by checking the return value of the external call or by calculating the pre- and post-swap balance difference.
        ```solidity
        // Secure Pattern
        uint256 amountReceived = router.swap(...);
        require(amountReceived >= minAmountOut, "Slippage limit exceeded");
        ```
    3.  **Transaction Deadlines:** Implement a timestamp deadline for transaction execution to prevent builders from withholding the transaction until market conditions become unfavorable.
    """

    STANDARD_JSON = False

    def _is_numeric(self, variable):
        """
        Checks if variable is numeric. 
        IMPORTANT: Always returns True for variables with NO type (like Assembly vars),
        otherwise we miss the Unoswap vulnerability.
        """
        if not variable: return False
        if not hasattr(variable, 'type'): return True # Assume Assembly var is risky
        if not variable.type: return True # Assume Assembly var is risky
        
        if isinstance(variable.type, ElementaryType):
            return variable.type.name.startswith("uint") or variable.type.name.startswith("int")
        return False

    def _is_active_source(self, ir):
        """
        Determines if an instruction is a relevant source of data (Swap or Balance).
        """
        # 1. Balance Checks (GenericRouter pattern)
        if isinstance(ir, (HighLevelCall, LibraryCall)):
            if 'balanceof' in str(ir.function_name).lower(): return True
        if isinstance(ir, SolidityCall) and 'balance' in ir.function.name:
            return True

        # 2. State Changing Calls (Swaps)
        # Exclude STATICCALLs to avoid false positives in OrderMixin/Predicates
        if isinstance(ir, (HighLevelCall, LibraryCall)):
            if hasattr(ir, 'function') and ir.function:
                if not (ir.function.view or ir.function.pure): return True
            # If unresolved, assume active unless flagged static
            elif not getattr(ir, 'is_static', False): return True

        if isinstance(ir, LowLevelCall):
            if ir.function_name in ['call', 'delegatecall']: return True
            
        return False

    def _detect(self):
        results = []

        for contract in self.slither.contracts:
            for function in contract.functions:
                
                # --- Step 1: Map Sources ---
                active_vars = set()
                
                for node in function.nodes:
                    # Assembly Handling (Unoswap V2)
                    if node.type == NodeType.ASSEMBLY:
                        node_str = str(node).lower()
                        # Capture CALLs, Ignore STATICCALLs
                        if "call(" in node_str and "staticcall(" not in node_str:
                            for var in node.variables_written:
                                # We treat assembly writes as active sources
                                active_vars.add(var)

                    # IR Handling
                    for ir in node.irs:
                        # Capture Calls and Balance Checks
                        if self._is_active_source(ir):
                             if ir.lvalue and self._is_numeric(ir.lvalue):
                                active_vars.add(ir.lvalue)
                                
                        # Capture Internal Wrappers (Unoswap V3)
                        # We blindly accept internal returns as potential sources to be safe
                        if isinstance(ir, InternalCall):
                            if ir.lvalue and self._is_numeric(ir.lvalue):
                                active_vars.add(ir.lvalue)

                if not active_vars:
                    continue

                # --- Step 2: Analyze Inequality Sinks ---
                for node in function.nodes:
                    if node.type != NodeType.IF: continue
                    
                    # FILTER: Only flag Inequalities (Slippage Logic)
                    # This removes "if (success)" checks
                    is_inequality = False
                    for ir in node.irs:
                        if isinstance(ir, Binary):
                            if ir.type in [BinaryType.LESS, BinaryType.LESS_EQUAL, BinaryType.GREATER, BinaryType.GREATER_EQUAL]:
                                is_inequality = True
                                break
                    if not is_inequality: continue

                    condition_vars = node.variables_read
                    
                    # Check 1: User Dependency
                    tainted_by_user = [p for p in function.parameters if any(is_dependent(v, p, contract) for v in condition_vars)]
                    if not tainted_by_user: continue

                    # Check 2: Active Source Dependency
                    tainted_by_source = []
                    for var in condition_vars:
                        for source in active_vars:
                            if is_dependent(var, source, contract):
                                tainted_by_source.append(source)
                                break
                    
                    if tainted_by_source:
                        # Final numeric check
                        if any(self._is_numeric(v) for v in condition_vars):
                            
                            param_names = list(set([p.name for p in tainted_by_user]))
                            
                            info = [
                                function,
                                f" Sandwich Opportunity Detected in '{function.name}' at line {node.source_mapping.lines}.\n"
                                f"\t- Logic: Inequality comparison (<, >, <=, >=) detected.\n"
                                f"\t- Compares Active Source (Swap/Balance) against User Input {param_names}"
                            ]
                            results.append(self.generate_result(info))

        return results