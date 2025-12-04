# Guia de Contribuição

Obrigado por considerar contribuir para este projeto! Este documento fornece diretrizes e instruções para ajudar você a contribuir de forma eficaz.

## Como Contribuir

### 1. Reportando Bugs

Se você encontrou um bug, por favor crie uma issue no repositório com as seguintes informações:

- **Título descritivo**: Um título claro e específico para o bug
- **Descrição detalhada**: Descreva exatamente o que aconteceu
- **Passos para reproduzir**: Forneça etapas específicas para reproduzir o problema
- **Comportamento esperado**: Descreva o que deveria acontecer
- **Comportamento atual**: O que realmente acontece
- **Screenshots**: Se aplicável, inclua screenshots
- **Ambiente**: Sistema operacional, versão do Python, etc.

### 2. Sugerindo Melhorias

Melhorias e novas funcionalidades são bem-vindas! Para sugerir uma melhoria:

1. Verifique se a melhoria já não foi sugerida
2. Crie uma issue com o rótulo `enhancement`
3. Descreva claramente a melhoria e sua motivação
4. Explique como esta melhoria seria útil para os usuários

### 3. Enviando Pull Requests

Passos para enviar um pull request:

#### Configuração do Ambiente

1. **Faça um fork do repositório**

   ```bash
   git clone https://github.com/WesleyQDev/cubinho.git
   cd cubinho
   ```

2. **Crie uma branch para sua funcionalidade**

   ```bash
   git checkout -b feature/sua-funcionalidade
   ```

3. **Configure o ambiente de desenvolvimento**
   ```bash
   uv sync
   ```

#### Desenvolvendo

- Siga o estilo de código existente do projeto
- Escreva código claro e bem documentado
- Adicione testes para novas funcionalidades
- Mantenha as mensagens de commit descritivas

#### Enviando o PR

1. **Faça commit das suas mudanças**

   ```bash
   git add .
   git commit -m "Descrição clara da mudança"
   ```

2. **Push para sua fork**

   ```bash
   git push origin feature/sua-funcionalidade
   ```

3. **Abra um Pull Request** no repositório original com:
   - Título claro e descritivo
   - Descrição detalhada das mudanças
   - Referência a qualquer issue relacionada
   - Screenshots se aplicável

## Padrões de Código

### Python

- Use **PEP 8** como guia de estilo
- Escreva docstrings em português para funções e classes
- Use type hints quando apropriado
- Nomes de variáveis em inglês
- Comentários explicativos em português

Exemplo:

```python
def calcular_soma(a: int, b: int) -> int:
    """
    Calcula a soma de dois números.

    Args:
        a: Primeiro número
        b: Segundo número

    Returns:
        A soma de a e b
    """
    return a + b
```

## Processo de Review

- Seu PR será revisado por mantenedores do projeto
- Feedback pode ser fornecido para melhorias
- Depois de aprovado, sua contribuição será merged
- Paciência é apreciada durante o processo de review

## Dúvidas?

- Abra uma issue com a tag `question`
- Descreva sua dúvida claramente
- Forneça contexto quando possível

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

Obrigado por contribuir e ajudar a melhorar este projeto! 🙏
