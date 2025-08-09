import os
import numpy as np
from scipy.spatial.distance import cosine
import pandas as pd
import re

def calculate_similarity(vector_a, vector_b):

    vector_a = vector_a.squeeze()
    vector_b = vector_b.squeeze()
    return 1 - cosine(vector_a, vector_b)

def load_embeddings(npy_path):

    data = np.load(npy_path, allow_pickle=True).item()
    for key in data:
        data[key] = data[key].squeeze()
    return data

def get_top_k_matches(test_vector, library_vectors, library_names, k=5):

    similarities = [(name, calculate_similarity(test_vector, vector))
                    for name, vector in zip(library_names, library_vectors)]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:k]

def evaluate_detection_rate(top_k_results, true_name):

    return [1 if true_name in [name for name, _ in top_k_results[:k]] else 0 for k in [1, 3, 5]]

def verify_embedding_dimensions(function_library, test_function):

    library_dims = set(tuple(vector.shape) for vector in function_library.values())
    test_dims = set(tuple(vector.shape) for vector in test_function.values())
    if len(library_dims) != 1 or len(test_dims) != 1:
        print("Warning: Inconsistent embedding dimensions detected.")
    else:
        print(f"All library embeddings have shape: {library_dims.pop()}")
        print(f"All test embeddings have shape: {test_dims.pop()}")

def write_results_to_txt(results, output_file):

    with open(output_file, 'w', encoding='utf-8') as f:
        for test_name, top_k_results in results.items():
            f.write(f"Test Function: {test_name}\n")
            f.write("Top-5 Similar Functions:\n")
            for name, similarity in top_k_results:
                f.write(f"  Function: {name}, Similarity: {similarity:.4f}\n")
            f.write("\n")

def parse_filename(filename):

    pattern = r'^([^_]+)_(.*)_embeddings\.npy$'
    match = re.match(pattern, filename)
    if match:
        obfuscation, method = match.groups()
        return obfuscation, method
    else:
        print(f"Warning: Filename {filename} does not match expected format")
        return None, None

def main():

    library_path = 'function_library_embeddings.npy'
    test_folder = '3_embedding_npy_fine_grain'
    result_folder = '4_detection_result'
    os.makedirs(result_folder, exist_ok=True)


    function_library = load_embeddings(library_path)
    library_names = list(function_library.keys())
    library_vectors = list(function_library.values())


    results = {}
    obfuscations = ['bcfobf', 'cffobf', 'o1', 'o2', 'o3', 'splitobf', 'subobf']


    test_files = [f for f in os.listdir(test_folder) if f.endswith('.npy')]
    if not test_files:
        print("No npy test files found in folder:", test_folder)
        return

    for test_file in test_files:
        test_path = os.path.join(test_folder, test_file)
        print(f"\nProcessing test file: {test_path}")
        test_function = load_embeddings(test_path)
        verify_embedding_dimensions(function_library, test_function)


        obfuscation, method = parse_filename(test_file)
        if not obfuscation or not method:
            continue


        if method not in results:
            results[method] = {obf: {'top-1': 0, 'top-3': 0, 'top-5': 0, 'count': 0} for obf in obfuscations}

        match_results = {}
        file_top1, file_top3, file_top5 = 0, 0, 0
        total_tests = len(test_function)

        # 计算每个待测函数的 Top-5 相似结果
        for test_name, test_vector in test_function.items():
            top_k_results = get_top_k_matches(test_vector, library_vectors, library_names, k=5)
            match_results[test_name] = top_k_results

            detection = evaluate_detection_rate(top_k_results, test_name)
            file_top1 += detection[0]
            file_top3 += detection[1]
            file_top5 += detection[2]

        # 写入当前 test_file 的结果到文本文件
        base_name = os.path.splitext(test_file)[0]
        output_file = os.path.join(result_folder, f"{base_name}_results.txt")
        write_results_to_txt(match_results, output_file)
        print(f"Results for {test_file} saved to {output_file}")

        # 更新结果字典
        if obfuscation in results[method]:
            results[method][obfuscation]['top-1'] = file_top1 / total_tests
            results[method][obfuscation]['top-3'] = file_top3 / total_tests
            results[method][obfuscation]['top-5'] = file_top5 / total_tests
            results[method][obfuscation]['count'] = total_tests

        # 输出当前文件的检测率
        print("Detection Rates for {}:".format(test_file))
        print(f"  Top-1 Detection Rate: {file_top1 / total_tests:.2%}")
        print(f"  Top-3 Detection Rate: {file_top3 / total_tests:.2%}")
        print(f"  Top-5 Detection Rate: {file_top5 / total_tests:.2%}")


    excel_path = os.path.join(result_folder, 'results.xlsx')
    data = []
    for method in results:
        for metric in ['top-1', 'top-3', 'top-5']:
            row = [method, metric]
            for obf in obfuscations:
                rate = results[method][obf][metric]
                row.append(f"{rate:.0%}" if rate > 0 else "0%")
            # 计算平均值
            valid_rates = [results[method][obf][metric] for obf in obfuscations if results[method][obf]['count'] > 0]
            avg = sum(valid_rates) / len(valid_rates) if valid_rates else 0
            row.append(f"{avg:.0%}")
            data.append(row)


    columns = ['method', 'Mterics'] + obfuscations + ['AVG']
    df = pd.DataFrame(data, columns=columns)
    df.set_index(['method', 'Mterics'], inplace=True)


    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Results')

    print(f"\nExcel results saved to {excel_path}")

if __name__ == '__main__':
    main()