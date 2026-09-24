# relatorio-cldf

Relatórios abertos e reprodutíveis sobre a Câmara Legislativa do Distrito Federal — derivados
exclusivamente de dados públicos, colhidos por requisições não autenticadas.

**Landing page:** `index.html` (GitHub Pages serve a raiz do repositório).

## Os três relatórios

| Endereço | O que é | Versão atual |
|---|---|---|
| `/dossie/` | Toda ocorrência de **BRB**, **Master** e **Vorcaro** no acervo aberto da CLDF, com o documento exato — 743 ocorrências em 66 proposições | v3 |
| `/tramitacao/` | A linha do tempo conjunta do **REQ 1965/2025** e do **PL 1882/2025**, e a resposta que nunca veio | v2 |
| `/dificuldades/` | O que existe, o que funciona, o que não funciona, o que está concentrado e fragmentado, e o que não atende à lei de transparência | v1 |

## Versionamento

Cada relatório tem **dois endereços**:

- `/<slug>/` — sempre a versão mais recente; muda a cada publicação;
- `/<slug>/vN/` — a versão N congelada, que **nunca muda** depois de publicada.

`versoes.json` é o manifesto: para cada versão, o caminho, a data, o tamanho e o **sha256** do
arquivo. Uma citação feita hoje continua verificável amanhã porque aponta para um `vN` cujo hash
está publicado.

Publicar uma nova versão de um relatório:

```sh
cp <novo.html> <slug>/vN+1/index.html   # a versão congelada
cp <novo.html> <slug>/index.html        # o ponteiro para a mais recente
python3 publicar.py                     # regenera versoes.json e index.html
```

`publicar.py` não tem dependência externa — só biblioteca padrão do Python 3.

## Os dados

`dados/` traz, em CSV e JSON, o que sustenta cada número dos relatórios:

| Arquivo | O que é |
|---|---|
| `pedidos-de-informacao.csv` | Os **1.231** requerimentos de informação do acervo, com o desfecho de cada um |
| `tipos-de-documento.csv` | Os **48** tipos de documento e quantos deles a API entrega legíveis |
| `ocorrencias.csv` | As 874 ocorrências brutas das três palavras-chave |
| `documentos.csv` | Os documentos do caso, com o endereço de origem de cada texto |
| `emendas.csv` | As nove emendas ao PL 1882/2025 |
| `votacoes.csv` | As votações nominais em que o caso aparece |
| `sessoes.csv` | As sessões em que o caso aparece |
| `anexos_pendentes.csv` | Os 68 documentos do caso que existem só como arquivo anexo |
| `contagens.json` | Todas as contagens da série, em JSON |

## Fontes

- API pública de proposições da CLDF — `ple.cl.df.gov.br`
- Portal de dados abertos da CLDF — `dados.cl.df.gov.br`
- Painéis do Portal da Transparência da CLDF
- Biblioteca Digital da CLDF — `biblioteca.cl.df.gov.br`

Nenhum sistema foi acessado com credencial e nenhuma informação restrita foi usada. Todo acesso
foi `GET` público, em série.

## Licenças

- **Código e interface:** uso não comercial.
- **Dados derivados:** CC BY-SA 4.0 — a mesma licença que a fonte declara, como a CC BY-SA exige
  de uma adaptação.
