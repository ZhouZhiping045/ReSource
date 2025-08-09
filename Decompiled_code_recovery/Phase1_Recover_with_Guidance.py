import argparse
from document_processor import read_queries, write_output
from prompt_templates import create_phase1_optimize_output_with_guidance
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import configparser
import os
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('decompiler_phase1.log'),
        logging.StreamHandler()
    ]
)

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CUR_DIR, 'DeepSeek_config.ini')


def load_llm_config() -> dict:

    required_keys = ['model', 'temperature', 'api_key', 'api_base']

    try:
        config = configparser.ConfigParser()
        if not config.read(CONFIG_FILE):
            raise FileNotFoundError(f"Config file {CONFIG_FILE} not found")

        if 'LLM' not in config:
            raise KeyError("Missing [LLM] section in config file")

        llm_config = dict(config['LLM'])


        missing = [k for k in required_keys if k not in llm_config]
        if missing:
            raise ValueError(f"Missing required keys: {missing}")


        llm_config['temperature'] = float(llm_config['temperature'])

        return llm_config

    except Exception as e:
        logging.error(f"Config loading failed: {str(e)}")
        raise


def read_and_split_queries(file_path: str) -> list:

    logging.info(f"Reading and splitting queries from {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [q.strip() for q in f.read().split('/////') if q.strip()]
    except UnicodeDecodeError:
        logging.error(f"Encoding error in {file_path}, trying gb2312...")
        with open(file_path, 'r', encoding='gb2312') as f:
            return [q.strip() for q in f.read().split('/////') if q.strip()]


def process_file(file_path: str, output_dir: str, llm: ChatOpenAI, template: str):

    try:
        queries = read_and_split_queries(file_path)
        results = []

        for idx, query in enumerate(queries, 1):
            logging.info(f"Processing query {idx}/{len(queries)} in {os.path.basename(file_path)}")

            try:
                prompt = template.format(code=query)
                response = llm.invoke([HumanMessage(content=prompt)])
                results.append(f"Query {idx}:\n{response.content.strip()}\n")
            except Exception as e:
                logging.error(f"Failed processing query {idx}: {str(e)}")
                results.append(f"Query {idx}:\n[ERROR] {str(e)}\n")


        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_step1.txt")
        write_output(output_path, "\n/////\n".join(results))

    except Exception as e:
        logging.error(f"Fatal error processing {file_path}: {str(e)}")


def main():

    try:
        llm_config = load_llm_config()
    except Exception as e:
        logging.critical("Failed to initialize configuration, exiting...")
        return


    try:
        llm = ChatOpenAI(
            model=llm_config['model'],
            temperature=llm_config['temperature'],
            openai_api_key=llm_config['api_key'],
            openai_api_base=llm_config['api_base']
        )
        logging.info(f"LLM initialized: {llm_config['model']} @ {llm_config['api_base']}")
    except Exception as e:
        logging.critical(f"LLM initialization failed: {str(e)}")
        return


    parser = argparse.ArgumentParser(
        description="AI Decompiler Assistant - Phase 1: Guidance Recovery",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--input_dir',
        type=str,
        default=os.path.join(os.getcwd(), 'Phase1_Decompiled_code_with_guidance'),
        help="Input directory containing phase1 processed files"
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default=os.path.join(os.getcwd(), 'Phase1_Decompiled_code_with_guidance_output'),
        help="Output directory for final results"
    )
    args = parser.parse_args()


    if not os.path.exists(args.input_dir):
        logging.critical(f"Input directory not found: {args.input_dir}")
        return

    os.makedirs(args.output_dir, exist_ok=True)


    try:
        correction_template = create_phase1_optimize_output_with_guidance()
        logging.info("Prompt template loaded successfully")
    except Exception as e:
        logging.critical(f"Template loading failed: {str(e)}")
        return


    processed_files = 0
    for root, _, files in os.walk(args.input_dir):
        for file in files:
            if not file.endswith('.txt'):
                continue

            file_path = os.path.join(root, file)
            logging.info(f"Processing {file_path}")

            try:
                process_file(file_path, args.output_dir, llm, correction_template)
                processed_files += 1
            except Exception as e:
                logging.error(f"Failed processing {file}: {str(e)}")

    logging.info(f"Process completed. {processed_files} files handled.")


if __name__ == "__main__":
    main()