"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do LangSmith Hub e salva localmente."""
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return False

    prompt_ref = "leonanluppi/bug_to_user_story_v1"
    output_path = "prompts/bug_to_user_story_v1.yml"

    print(f"Fazendo pull do prompt: {prompt_ref}")

    try:
        prompt = hub.pull(prompt_ref)
        print("✓ Prompt carregado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False

    messages = prompt.messages
    system_prompt = ""
    user_prompt = ""

    for msg in messages:
        role = msg.__class__.__name__.lower()
        content = msg.prompt.template if hasattr(msg, "prompt") else str(msg)
        if "system" in role:
            system_prompt = content
        elif "human" in role:
            user_prompt = content

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "source": prompt_ref,
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if save_yaml(prompt_data, output_path):
        print(f"✓ Prompt salvo em: {output_path}")
        return True
    else:
        print(f"❌ Falha ao salvar prompt em: {output_path}")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    success = pull_prompts_from_langsmith()

    if success:
        print("\n✅ Pull concluído com sucesso!")
        print("Próximo passo: otimize o prompt em prompts/bug_to_user_story_v2.yml")
        return 0
    else:
        print("\n❌ Pull falhou. Verifique as mensagens acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
