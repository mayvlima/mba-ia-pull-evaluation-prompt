"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurada no .env")
        return False

    full_name = f"{username}/{prompt_name}"
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    print(f"Fazendo push do prompt: {full_name}")

    try:
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(user_prompt),
        ])

        tags = prompt_data.get("tags", [])
        techniques = prompt_data.get("techniques_applied", [])
        description = prompt_data.get("description", "")
        all_tags = list(set(tags + techniques))

        hub.push(
            full_name,
            chat_prompt,
            new_repo_description=description,
            new_repo_is_public=True,
            tags=all_tags,
        )

        print(f"✓ Prompt publicado com sucesso: {full_name}")
        print(f"  Tags: {', '.join(all_tags)}")
        print(f"  Acesse em: https://smith.langchain.com/hub/{full_name}")
        return True

    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA O LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    yaml_path = "prompts/bug_to_user_story_v2.yml"
    raw = load_yaml(yaml_path)

    if raw is None:
        print(f"❌ Arquivo não encontrado ou inválido: {yaml_path}")
        print("Crie o arquivo prompts/bug_to_user_story_v2.yml antes de continuar.")
        return 1

    # O YAML pode ter a chave aninhada (bug_to_user_story_v2: {...}) ou estar no nível raiz
    if "bug_to_user_story_v2" in raw:
        prompt_data = raw["bug_to_user_story_v2"]
    else:
        prompt_data = raw

    print("Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Prompt válido")

    success = push_prompt_to_langsmith("bug_to_user_story_v2", prompt_data)

    if success:
        print("\n✅ Push concluído com sucesso!")
        print("Próximo passo: execute python src/evaluate.py")
        return 0
    else:
        print("\n❌ Push falhou. Verifique as mensagens acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
