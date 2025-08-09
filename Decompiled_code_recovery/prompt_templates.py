from langchain.prompts import PromptTemplate
def create_phase1_optimize_output_with_guidance():
    template = """As an experienced reverse engineering and code optimization expert, please help me analyze the decompiled code. After decompiling, there will be guidance for fixing the discrepancies based on the comparison with the source code, but some may also be false positives. Please consider the guidance based on the possible semantic differences between the decompiled function and the source code, and restore the decompiled code to match the source code.
Output Requirements:
Please output the fixed decompiled code without changing function names, without adding comments, and without explanations.
Output Format:
Fixed decompiled code:
The decompiled code is as follows:
{code}
    """
    return PromptTemplate.from_template(template)

def create_phase2_optimize_output_with_cfs():
    template = """As an experienced reverse engineering and code optimization expert, please help me analyze the decompiled code.
Please refer to the predicted control flow structure and restore the decompiled code to the source code.
Output Requirements:
Output the fixed decompiled code without changing function names, without adding comments, and without explanations.
{code}
    """
    return PromptTemplate.from_template(template)

def create_phase3_final_recovery():
    template = """As a professional program analyst, please help me review the following decompiled code and restore it to the original code, checking for the following issues:
1. Restore function return types, variables, and parameter types to conventional types, especially for struct field accesses.
2. Eliminate redundant variables and code, and simplify variable and parameter names according to naming conventions and intentions.
3. Simplify the code structure by removing meaningless loops and branch structures.
4. Restore specific constants to macros that follow programming conventions, especially boundary values and magic numbers.
5. Remove compiler-specific mechanisms (such as __assert_fail, error(), __readgsdword, etc.).
6. Simplify control flow.
7. Ensure that the function's readability meets the requirements for program delivery.
Output Requirements:

Only output the fixed decompiled code without explanations.

The decompiled code is as follows:
    {code}
    """
    return PromptTemplate.from_template(template)


def create_Construct_Semantic_Distortion_Database_template():
    template = """As a reverse engineering expert, please help me align the following source code with the decompiled function code pairs:
{code}
Focus only on the semantic differences between the code pairs, and output the differences in the following format:
“##distortion_type##decompiled code line##source code line##reason”, with no comments or additional explanations. 
    """
    return PromptTemplate.from_template(template)

def create_fix_comment_template():
    template = """As a reverse engineering expert, please help me construct a Semantic Distortion Database for identifying distortions in decompiled code in closed-source environments.
Please assist me with processing the following source code functions and their corresponding decompiled function pairs:
{code}
Please strictly align the above source code functions and decompiled code, analyzing the decompiled code line by line starting from the function signature, focusing only on semantic distortions. Output the distortion types as required:
Semantic: Includes return value and function semantic differences (semantic_return), error handling mechanisms (error_safety), condition checks (condition_check), control flow differences (control_flow), state management and initialization (state_management), redundant code (optimization_redundancy), function call differences (function_call), and memory usage differences (memory_usage).
Carefully examine each line of decompiled code to ensure you analyze the code line by line starting from the function signature, avoiding false positives and omissions. The requirements are:
Analyze the decompiled code line by line, outputting all code lines with semantic distortions in the following format:
“##distortion_type##decompiled_line_number##decompiled code line##source_line_number##source code line”, where:
decompiled_line_number is the line number of the decompiled code (starting from 1);
decompiled code line is the line of decompiled code with semantic distortion;
source_line_number is the corresponding source code line number (starting from 1), or "none" if there is no matching line;
source_code_line is the corresponding source code line, or "none" if there is no matching line.
Example: ##state_management##5##*(_QWORD *)(v12 + 328) = 0LL;##3##cctx->str = NULL; ##optimization_redundancy##2##__int64 v12;##none##none
The same line of decompiled code may have multiple semantic distortion types; output each distortion type on a separate line.
Do not generate fix suggestions, only output the distortion information.
The categorization rules are as follows:
semantic_return: Used only for return statements where the return behavior does not match the source code; must check return statements.
error_safety: Used only for explicit error handling mechanism differences (e.g., _assert_fail, error(), __readgsdword, etc.).
condition_check: Used for logical differences in condition statements (e.g., if, while) that do not match the source code; all condition statements must be identified.
control_flow: Used for control flow structure differences (e.g., if-else, do-while) that do not match the source code; must check whether control flow structures are missing or altered.
state_management: Used only for struct or state variable initialization/update operations (e.g., *(_QWORD *)(v12 + 328) = 0LL;), excluding normal variable assignments (e.g., v14 = v12 + 272;) or pointer operations (e.g., v12 = *(_QWORD *)(a1 + 120);).
optimization_redundancy: Used for all redundant code, including redundant variable declarations (e.g., __int64 v12;), redundant assignments (e.g., v14 = v12 + 272;), unnecessary computations (e.g., v13 = 8 * *(_DWORD *)(a1 + 104);), and extra variables or operations that do not exist in the source code; must identify all redundant variables, assignments, and computations.
function_call: Used for function call statements (e.g., vpaes_set_encrypt_key(...)), including function calls in assignment form (e.g., v17 = vpaes_encrypt;), but excluding regular assignments or pointer dereferencing; all function call differences must be identified.
memory_usage: Used for memory operations (e.g., memcpy, free, etc.) that do not match the source code.
If a new semantic distortion type is discovered, output it in the following format:
“99.new_type##decompiled_line_number##decompiled code line##source_line_number##all_source_code code line##New Type: Description”.
Ensure that all possible semantic distortion types are identified, especially semantic_return, condition_check, control_flow, state_management, optimization_redundancy, and function_call.
Analyze the decompiled code line by line starting from the first line (function signature) to ensure no distortion is missed.
Do not output any explanations or additional information.
"""
    return PromptTemplate.from_template(template)
def create_fix_suggestion_template():
    template = """As a program analysis expert, analyze the distorted code lines below and the corresponding source code functions, and generate fix suggestions for the given decompiled distortion types. The distorted code lines include: distortion type##line number##source code.
{code}
Requirements:
Do not output any explanations or additional information.
The suggestions must be abstract and general, providing repair guidance for other similar semantic cases, with concise descriptions in English.
Output in the specified JSON format, and standardize function names, variable names, and parameter names.
"output_format":
{
  "code_line_number": "<line_number>",
  "code_line": "<original_code_line_text>",
  "operation_type": "<standardized_operation_type>",
  "target": "<standardized_target_object_of_operation, e.g., Structure->member>",
  "all_source_code": "<standardized_source_object_of_operation, e.g., Var_0>",
  "data_transfer": "<standardized_data_flow_direction>",
  "control_flow": "<standardized_control_flow_effect>",
  "function_context": "<standardized_function_context_relation>",
  "global_effects": "<side_effects>",
  "inputs": ["<standardized_dependency_variable_1, e.g., Param_0>", "<standardized_dependency_variable_2, e.g., Var_0>"],
  "state_changes": "<modifications_to_program_state>",
  "guidance": ["<guidance_suggestion_1>", "<guidance_suggestion_2>"]
}
Optimization Rules:
Field names should be standardized and clear.
Content should be normalized.
Do not output empty fields to avoid redundancy.
Maintain structured JSON output for easy parsing.
"""
    return PromptTemplate.from_template(template)






