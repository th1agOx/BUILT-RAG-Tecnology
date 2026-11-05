"""Testes de arquitetura: regras de importação do ADR-0003 (R1 a R6).

Cada teste começa com uma docstring de uma linha contendo a pergunta de negócio
e cita a regra (R1 a R6). A metodologia segue a Etapa 4 da US-00: copia o
esqueleto para um diretório temporário, injeta o import indicado e confirma o
resultado esperado. O repositório real nunca recebe o import ruim.
"""

from __future__ import annotations

import ast
import shutil
import sys
from pathlib import Path

import pytest
from importlinter.cli import lint_imports

SRC_BUILT = Path("src/built")
PYPROJECT = Path("pyproject.toml")

STDLIB = set(sys.stdlib_module_names)

# R2: policy/domain só importa stdlib, built.shared_kernel, ele mesmo e built.policy.published
R2_PERMITIDOS = STDLIB | {
    "built.shared_kernel",
    "built.policy.domain",
    "built.policy.published",
}
# R3: shared_kernel só importa stdlib e si mesmo
R3_PERMITIDOS = STDLIB | {"built.shared_kernel"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def copiar_esqueleto(tmp_path: Path) -> Path:
    """Copia src/built e pyproject.toml para um diretório temporário."""
    destino = tmp_path / "projeto"
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC_BUILT, destino / "src" / "built")
    shutil.copy2(PYPROJECT, destino / "pyproject.toml")
    return destino


def injetar_import(arquivo: Path, linha: str) -> None:
    """Injeta uma linha de import no arquivo, após o conteúdo existente."""
    conteudo = arquivo.read_text(encoding="utf-8")
    if not conteudo.endswith("\n"):
        conteudo += "\n"
    arquivo.write_text(conteudo + linha + "\n", encoding="utf-8")


def extrair_imports_modulo(conteudo: str) -> list[str]:
    """Extrai nomes de módulos de nível superior a partir do fonte Python."""
    imports: list[str] = []
    try:
        tree = ast.parse(conteudo)
    except SyntaxError:
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    return imports


def verificar_lista_permitida(diretorio_src: Path, permitidos: set[str]) -> list[str]:
    """Retorna lista de imports fora da lista permitida em todos os .py do diretório."""
    falhas: list[str] = []
    for arquivo in sorted(diretorio_src.rglob("*.py")):
        conteudo = arquivo.read_text(encoding="utf-8")
        for imp in extrair_imports_modulo(conteudo):
            if imp not in permitidos:
                falhas.append(f"{arquivo}: {imp}")
    return falhas


def executar_importlinter(diretorio_projeto: Path, monkeypatch: pytest.MonkeyPatch) -> int:
    """Executa o import-linter dentro do diretório do projeto copiado."""
    monkeypatch.chdir(diretorio_projeto)
    src_path = diretorio_projeto / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    return lint_imports()


# ---------------------------------------------------------------------------
# Casos 1-7: injeção com resultado esperado de FALHA
# ---------------------------------------------------------------------------


def test_dominio_policy_nao_pode_importar_infraestrutura_propria(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """O domínio do policy pode importar a infraestrutura dele? (R1)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "policy" / "domain" / "__init__.py"
    injetar_import(alvo, "from built.policy import infrastructure")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 1, "R1 esperava falha: policy.domain não deve importar policy.infrastructure"


def test_dominio_policy_nao_pode_importar_httpx(
    tmp_path: Path,
):
    """O domínio do policy pode importar bibliotecas externas como httpx? (R2)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "policy" / "domain" / "__init__.py"
    injetar_import(alvo, "import httpx")
    falhas = verificar_lista_permitida(
        projeto / "src" / "built" / "policy" / "domain", R2_PERMITIDOS
    )
    assert falhas, "R2 esperava falha: policy.domain não deve importar httpx"


def test_shared_kernel_nao_pode_importar_policy_published(
    tmp_path: Path,
):
    """O shared_kernel pode importar o vocabulário público do policy? (R3)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "shared_kernel" / "__init__.py"
    injetar_import(alvo, "from built.policy import published")
    falhas = verificar_lista_permitida(projeto / "src" / "built" / "shared_kernel", R3_PERMITIDOS)
    assert falhas, "R3 esperava falha: shared_kernel não deve importar built.policy.published"


def test_shared_kernel_nao_pode_importar_httpx(
    tmp_path: Path,
):
    """O shared_kernel pode importar bibliotecas externas como httpx? (R3)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "shared_kernel" / "__init__.py"
    injetar_import(alvo, "import httpx")
    falhas = verificar_lista_permitida(projeto / "src" / "built" / "shared_kernel", R3_PERMITIDOS)
    assert falhas, "R3 esperava falha: shared_kernel não deve importar httpx"


def test_pipeline_rag_nao_pode_importar_policy_domain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """O pipeline do rag pode importar o domínio do policy? (R4)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "infrastructure" / "rag" / "pipeline.py"
    injetar_import(alvo, "from built.policy import domain")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 1, "R4 esperava falha: rag.pipeline não deve importar policy.domain"


def test_gate_rag_nao_pode_importar_qdrant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """O gate do rag pode importar o adaptador do Qdrant? (R5)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "infrastructure" / "rag" / "gate.py"
    injetar_import(alvo, "from built.infrastructure.adapters import qdrant")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 1, "R5 esperava falha: rag.gate não deve importar adapters.qdrant"


def test_pipeline_rag_nao_pode_importar_adapter_llm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """O pipeline do rag pode importar o adaptador de LLM? (R6)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "infrastructure" / "rag" / "pipeline.py"
    injetar_import(alvo, "from built.infrastructure.adapters import llm")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 1, "R6 esperava falha: rag.pipeline não deve importar adapters.llm"


# ---------------------------------------------------------------------------
# Casos 8-13: injeção com resultado esperado de PASSA
# ---------------------------------------------------------------------------


def test_dominio_policy_pode_importar_json(
    tmp_path: Path,
):
    """O domínio do policy pode importar json da biblioteca padrão? (R2)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "policy" / "domain" / "__init__.py"
    injetar_import(alvo, "import json")
    falhas = verificar_lista_permitida(
        projeto / "src" / "built" / "policy" / "domain", R2_PERMITIDOS
    )
    assert not falhas, f"R2 esperava passa: policy.domain pode importar json. Falhas: {falhas}"


def test_pipeline_rag_pode_importar_policy_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """O pipeline do rag pode importar o vocabulário público do policy? (R4)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "infrastructure" / "rag" / "pipeline.py"
    injetar_import(alvo, "from built.policy import published")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 0, "R4 esperava passa: rag.pipeline pode importar policy.published"


def test_gate_rag_pode_importar_policy_application(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """O gate do rag pode importar os casos de uso do policy? (R4)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "infrastructure" / "rag" / "gate.py"
    injetar_import(alvo, "from built.policy import application")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 0, "R4 esperava passa: rag.gate pode importar policy.application"


def test_ingestion_pode_importar_qdrant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A ingestão do knowledge pode importar o adaptador do Qdrant? (R5)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "knowledge" / "ingestion" / "__init__.py"
    injetar_import(alvo, "from built.infrastructure.adapters import qdrant")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 0, "R5 esperava passa: knowledge.ingestion pode importar adapters.qdrant"


def test_entrypoints_pode_importar_qdrant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Os entrypoints podem importar o adaptador do Qdrant? (R5)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "entrypoints" / "__init__.py"
    injetar_import(alvo, "from built.infrastructure.adapters import qdrant")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 0, "R5 esperava passa: entrypoints pode importar adapters.qdrant"


def test_adapter_llm_pode_importar_rag_ports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """O adaptador de LLM pode importar as portas do rag? (R6)"""
    projeto = copiar_esqueleto(tmp_path)
    alvo = projeto / "src" / "built" / "infrastructure" / "adapters" / "llm" / "__init__.py"
    injetar_import(alvo, "from built.infrastructure.rag import ports")
    codigo = executar_importlinter(projeto, monkeypatch)
    assert codigo == 0, "R6 esperava passa: adapters.llm pode importar rag.ports"


# ---------------------------------------------------------------------------
# Regras R2 e R3 aplicadas ao esqueleto real (sem injeção)
# ---------------------------------------------------------------------------


def test_dominio_policy_respeita_lista_permitida_r2():
    """O domínio do policy respeita a lista de imports permitida? (R2)"""
    falhas = verificar_lista_permitida(SRC_BUILT / "policy" / "domain", R2_PERMITIDOS)
    assert not falhas, f"R2 no esqueleto real: {falhas}"


def test_shared_kernel_respeita_lista_permitida_r3():
    """O shared_kernel respeita a lista de imports permitida? (R3)"""
    falhas = verificar_lista_permitida(SRC_BUILT / "shared_kernel", R3_PERMITIDOS)
    assert not falhas, f"R3 no esqueleto real: {falhas}"
