"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_prompt_data() -> dict:
    """Retorna o dict de dados do prompt v2, independente do nível de aninhamento."""
    raw = load_prompts(str(PROMPT_PATH))
    if "bug_to_user_story_v2" in raw:
        return raw["bug_to_user_story_v2"]
    return raw


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        data = get_prompt_data()
        assert "system_prompt" in data, "Campo 'system_prompt' não encontrado no YAML"
        assert data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "").lower()
        role_keywords = ["você é", "you are", "product manager", "especialista", "sênior", "senior"]
        has_role = any(kw in system_prompt for kw in role_keywords)
        assert has_role, (
            "O system_prompt não define uma persona/role. "
            "Adicione algo como 'Você é um Product Manager sênior...'"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "").lower()
        format_keywords = ["user story", "como um", "como o", "critérios de aceitação",
                           "dado que", "quando", "então", "markdown", "formato"]
        has_format = any(kw in system_prompt for kw in format_keywords)
        assert has_format, (
            "O system_prompt não menciona o formato de saída esperado. "
            "Especifique o formato User Story ou Markdown."
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "")
        # Conta quantos blocos de exemplo existem
        example_markers = ["Exemplo", "Example", "Relato de bug:", "User Story gerada:"]
        count = sum(system_prompt.count(marker) for marker in example_markers)
        assert count >= 2, (
            "O system_prompt deve conter pelo menos 1 exemplo completo de Few-shot "
            "(com 'Relato de bug' e 'User Story gerada'). "
            f"Encontrados {count} marcadores de exemplo."
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "")
        user_prompt = data.get("user_prompt", "")
        full_text = system_prompt + user_prompt
        assert "[TODO]" not in full_text, "Encontrado '[TODO]' no prompt — remova antes de publicar"
        assert "TODO" not in full_text, "Encontrado 'TODO' no prompt — remova antes de publicar"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        data = get_prompt_data()
        techniques = data.get("techniques_applied", [])
        assert isinstance(techniques, list), "Campo 'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied', "
            f"encontradas: {len(techniques)} — {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
