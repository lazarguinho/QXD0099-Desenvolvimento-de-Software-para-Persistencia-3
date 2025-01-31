# QXD0099-Desenvolvimento-de-Software-para-Persistencia-3


```
erDiagram
    Usuario ||--|| Carrinho : possui
    Usuario ||--o{ Pedido : faz
    Categoria ||--o{ Produto : contem
    Pedido ||--o{ Avaliacao : tem
    Produto }o--o{ Carrinho : "esta em"
    Produto }o--o{ Pedido : "esta em"

    Usuario {
        string id
        string nome
        string email
        string senha
        string endereco
        string telefone
    }

    Produto {
        string id
        string nome
        string descricao
        float preco
        int quantidade_estoque
        string categoria
    }

    Pedido {
        string id
        date data
        string status
        float valor_total
        string metodo_pagamento
        float frete
    }

    Carrinho {
        string id
        date data_criacao
        float subtotal
        int quantidade_items
        string status
    }

    Avaliacao {
        string id
        int nota
        string comentario
        date data
        string status
        string titulo
    }

    Categoria {
        string id
        string nome
        string descricao
        string status
        string nivel_categoria
    }
```

Bancos de dados não relacional - MongoDB
