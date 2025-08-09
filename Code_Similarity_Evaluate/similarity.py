import os
import re
import math
import logging
from tree_sitter import Language, Parser
from anytree import Node, RenderTree
from Levenshtein import distance as levenshtein_distance

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory paths
SOURCE_DIR = "0-sourcecode"
OPTIMIZED_DIR = "fine_grain_final_output2txt"

# Initialize tree-sitter parser
C_LANGUAGE = Language('tree-sitter-c/build/my-languages.dll', 'c')
parser = Parser()
parser.set_language(C_LANGUAGE)


def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist!")
    return True


def read_file(file_path):
    check_file_exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_functions(file_path):
    content = read_file(file_path).strip()
    funcs = [func.strip() for func in content.split("/////") if func.strip()]
    return funcs


def extract_signature(code):
    match = re.search(r'^(.*?)\{', code, re.DOTALL)
    if match:
        signature = match.group(1).strip()
        return re.sub(r'\s+', ' ', signature)
    return ""


def extract_interface(code):
    sig = extract_signature(code)
    m = re.search(r'^(.*?)\s+([A-Za-z_]\w*)\s*\((.*?)\)', sig)
    if m:
        return {
            'return_type': m.group(1).strip(),
            'name': m.group(2).strip(),
            'params': m.group(3).strip()
        }
    return {'return_type': '', 'name': '', 'params': ''}


def interface_similarity(intf1, intf2):
    def norm_sim(s1, s2):
        max_len = max(len(s1), len(s2), 1)
        return 1 - (levenshtein_distance(s1, s2) / max_len)

    # 返回类型语义映射
    return_type_mapping = {
        'int': ['MagickBooleanType', 'bool'],
        'MagickBooleanType': ['int', 'bool'],
        'bool': ['int', 'MagickBooleanType'],
        'uint8_t': ['unsigned char'],
        'unsigned char': ['uint8_t']
    }

    def normalize_type(type_str):
        for key, equivalents in return_type_mapping.items():
            if type_str == key or type_str in equivalents:
                return key
        return type_str

    name_sim = norm_sim(intf1['name'], intf2['name'])
    ret_sim = norm_sim(normalize_type(intf1['return_type']), normalize_type(intf2['return_type']))
    param_sim = norm_sim(intf1['params'], intf2['params'])
    sim = 0.4 * name_sim + 0.3 * ret_sim + 0.3 * param_sim
    return sim


def parse_c_code(code):
    try:
        tree = parser.parse(code.encode('utf-8'))
        return tree
    except Exception as e:
        logging.error(f"解析代码时出错：{e}")
        raise


def tree_sitter_to_anytree(node, parent=None):
    if node is None:
        return None
    node_type = node.type
    if node_type == 'call_expression':
        try:
            func_name = node.child_by_field_name('function').text.decode('utf-8')
            if func_name in ('fwrite', 'WriteBlobByte', 'fputc'):
                node_type = 'write_operation'
        except:
            pass
    new_node = Node(node_type, parent=parent)
    for child in node.children:
        tree_sitter_to_anytree(child, parent=new_node)
    return new_node


def compute_tree_edit_distance(tree1, tree2):
    root1 = tree_sitter_to_anytree(tree1.root_node)
    root2 = tree_sitter_to_anytree(tree2.root_node)

    def tree_to_string(tree):
        return ''.join(f"{node.name}" for _, _, node in RenderTree(tree))

    str1 = tree_to_string(root1)
    str2 = tree_to_string(root2)
    max_len = max(len(str1), len(str2))
    if max_len == 0:
        return 1.0
    edit_dist = levenshtein_distance(str1, str2)
    similarity = 1 - (edit_dist / max_len)
    return max(0, similarity)


def extract_control_flow(code):
    tree = parse_c_code(code)
    control_nodes = []

    def traverse(node):
        if node.type in (
        'if_statement', 'for_statement', 'while_statement', 'do_statement', 'switch_statement', 'return_statement'):
            control_nodes.append(node.type)
        for child in node.children:
            traverse(child)

    traverse(tree.root_node)
    return sorted(control_nodes)


def control_flow_similarity(cf1, cf2):
    str1 = ''.join(cf1)
    str2 = ''.join(cf2)
    max_len = max(len(str1), len(str2), 1)
    edit_dist = levenshtein_distance(str1, str2)
    sim = 1 - (edit_dist / max_len)
    return sim


def compute_halstead_metrics(code):
    try:
        tree = parse_c_code(code)
        root = tree.root_node
        operators = set()
        operands = set()
        op_count = 0
        opd_count = 0

        def traverse(node):
            nonlocal op_count, opd_count
            if node.type in (
            '+', '-', '*', '/', '%', '=', '==', '!=', '>', '<', '>=', '<=', '&&', '||', '!', '++', '+=', '-=', '->',
            ':', '?'):
                operators.add(node.type)
                op_count += 1
            elif node.type in ('if', 'for', 'while', 'do', 'return'):
                operators.add(node.type)
                op_count += 1
            elif node.type == 'call_expression':
                operators.add('()')
                op_count += 1
            elif node.type == 'subscript_expression':
                operators.add('[]')
                op_count += 1
            elif node.type in ('identifier', 'number_literal'):
                try:
                    text = node.text.decode('utf-8')
                except:
                    text = str(node.text)
                operands.add(text)
                opd_count += 1
            for child in node.children:
                traverse(child)

        traverse(root)
        n1 = len(operators)
        n2 = len(operands)
        N1 = op_count
        N2 = opd_count
        n = n1 + n2
        N = N1 + N2
        volume = N * (math.log2(n) if n > 0 else 0)
        difficulty = (n1 / 2) * (N2 / (n2 if n2 != 0 else 1))
        effort = volume * difficulty
        return {'volume': volume, 'difficulty': difficulty, 'effort': effort}
    except Exception as e:
        logging.error(f"Error calculating Halstead metric: {e}")
        raise


def halstead_similarity(metrics1, metrics2):
    vol1 = metrics1.get('volume', 0)
    vol2 = metrics2.get('volume', 0)
    if vol1 == 0 and vol2 == 0:
        return 1.0
    diff = abs(vol1 - vol2)
    sim = 1 - (diff / max(vol1, vol2))
    return sim


def extract_tokens(code):
    tree = parser.parse(bytes(code, 'utf8'))
    root_node = tree.root_node
    tokens = []

    def traverse(node):
        if node.type == 'identifier':
            tokens.append('VAR')
        elif node.type in ('number_literal', 'string_literal'):
            tokens.append(node.text.decode('utf8'))
        elif node.type in (
                '+', '-', '*', '/', '=', '==', '!=', '>', '<', '>=', '<=', '&&', '||', '!', '++', '+=', '-=', '->',
                ':', '?'):
            tokens.append(node.type)
        for child in node.children:
            traverse(child)

    traverse(root_node)
    return tokens


def compute_token_edit_distance(code1, code2):
    tokens1 = extract_tokens(code1)
    tokens2 = extract_tokens(code2)
    edit_dist = levenshtein_distance(tokens1, tokens2)
    max_len = max(len(tokens1), len(tokens2))
    similarity = 1 - (edit_dist / max_len) if max_len > 0 else 1
    return similarity


def normalize_code(code):
    code = re.sub(r'\bfwrite\b', 'WriteBlobByte', code)
    code = re.sub(r'\bfputc\b', 'WriteBlobByte', code)
    code = re.sub(r'\buint8_t\b', 'unsigned char', code)
    return code


def evaluate_function_similarity(source_code, test_code):
    source_code = normalize_code(source_code)
    test_code = normalize_code(test_code)
    source_intf = extract_interface(source_code)
    test_intf = extract_interface(test_code)
    intf_sim = interface_similarity(source_intf, test_intf)
    source_tree = parse_c_code(source_code)
    test_tree = parse_c_code(test_code)
    struct_sim = compute_tree_edit_distance(source_tree, test_tree)
    cf_source = extract_control_flow(source_code)
    cf_test = extract_control_flow(test_code)
    ctrl_sim = control_flow_similarity(cf_source, cf_test)
    source_halstead = compute_halstead_metrics(source_code)
    test_halstead = compute_halstead_metrics(test_code)
    halstead_sim = halstead_similarity(source_halstead, test_halstead)
    token_edit_sim = compute_token_edit_distance(source_code, test_code)
    overall = (0.2 * intf_sim + 0.15 * struct_sim + 0.2 * ctrl_sim +
               0.3 * halstead_sim + 0.15 * token_edit_sim)
    return {
        'interface_similarity': intf_sim,
        'structure_similarity': struct_sim,
        'control_flow_similarity': ctrl_sim,
        'halstead_similarity': halstead_sim,
        'token_edit_similarity': token_edit_sim,
        'overall_similarity': overall
    }


def evaluate_file_pair(source_file, test_file):
    source_funcs = read_functions(source_file)
    test_funcs = read_functions(test_file)
    if len(source_funcs) != len(test_funcs):
        logging.warning(f"The number of functions in files {source_file} and {test_file} does not match!")
        return None
    sim_scores = {
        'interface': [],
        'structure': [],
        'control_flow': [],
        'halstead': [],
        'token_edit': [],
        'overall': []
    }
    skipped = 0
    for i, (s_func, t_func) in enumerate(zip(source_funcs, test_funcs), start=1):
        if s_func == "null" or t_func == "null":
            logging.info(f"Skip function {i}: The source function or optimization function is null")
            skipped += 1
            continue
        try:
            sim = evaluate_function_similarity(s_func, t_func)
            sim_scores['interface'].append(sim['interface_similarity'])
            sim_scores['structure'].append(sim['structure_similarity'])
            sim_scores['control_flow'].append(sim['control_flow_similarity'])
            sim_scores['halstead'].append(sim['halstead_similarity'])
            sim_scores['token_edit'].append(sim['token_edit_similarity'])
            sim_scores['overall'].append(sim['overall_similarity'])
        except Exception as e:
            logging.error(f"Error processing function {i}: {e}")
            for key in sim_scores:
                sim_scores[key].append(0)
    if not sim_scores['overall']:
        logging.warning(f"There are no valid function pairs for comparing files {source_file} and {test_file}")
        return None
    avg_scores = {key: sum(values) / len(values) for key, values in sim_scores.items()}
    logging.info(f"File {source_file}: Processing {len(sim_scores['overall'])} functions, skipping {skipped} null functions")
    return avg_scores


def evaluate_all_files():
    source_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('_source.txt')]
    if not source_files:
        logging.warning("No files that meet the criteria were found in the source folder. ")
        return
    for src_filename in sorted(source_files):
        base_name = src_filename.replace('_source.txt', '')
        test_filename = f"{base_name}_fine_grain_final.txt"
        src_path = os.path.join(SOURCE_DIR, src_filename)
        test_path = os.path.join(OPTIMIZED_DIR, test_filename)
        if not os.path.exists(test_path):
            logging.warning(f"No corresponding optimization file found: {test_path}")
            continue
        try:
            avg_sim = evaluate_file_pair(src_path, test_path)
            if avg_sim is not None:
                print(f"Average similarity of file {src_filename}: ")
                print(f"  Interface similarity: {avg_sim['interface']:.4f}")
                print(f"  Structure similarity: {avg_sim['structure']:.4f}")
                print(f"  Control flow similarity: {avg_sim['control_flow']:.4f}")
                print(f"  Halstead similarity: {avg_sim['halstead']:.4f}")
                print(f"  Token edit similarity: {avg_sim['token_edit']:.4f}")
                print(f" Overall similarity: {avg_sim['overall']:.4f}")
        except Exception as e:
            logging.error(f"Error processing file {src_filename}: {e}")


if __name__ == "__main__":
    try:
        evaluate_all_files()
    except Exception as e:
        logging.error(f"Error occurred during the evaluation process: {e}")