# Hiring Challenge (Soft. Engineers Backend) - Take Home

Desafio técnico para a posição de Software Engineering Full-stack.

# 📄 Sumário

---

# Sobre o teste

Nesse teste, esperamos que ele tenha duração de no máximo 1:30h e iremos simular os requisitos técnicos para a construção de uma *feature* que temos na plataforma da Kanastra. Essa funcionalidade envolve um api de *upload* de arquivos, a que processa arquivos muitos grandes de forma performática

No momento do teste, você receberá todos os detalhes e requisitos necessários.

# Instruções iniciais

- Para ***backend,*** a **linguagem** e **IDE** que irá utilizar é uma decisão completamente **pessoal** do candidato, aqui na Kanastra nós amamos as linguagens PHP, TypeScript e Python!
- Recomendamos utilizar frameworks de desenvolvimento. Aqui na Kanastra nós utilizamos alguns como: Laravel, Django e FastAPI.

<aside>
🚨 Se você é um Software Engineer pleno, Sr. Software Engineer, ou tem senioridade ainda maior, **Unit and integration tests** são mandatórios nos deasfios para casa. Não aceitaremos cases sem eles.

</aside>

# 🎯 Desafio

Você faz parte de um *tech squad* da Kanastra e recebeu o desafio de construir um sistema de cobranças na plataforma. Esse sistema precisa ser capaz de cumprir os seguintes requisitos:

### Backend

- **Criar um *endpoint*** da API processar o arquivo;
    - Na Kanastra, processamos muitos registros e precisamos de escala. Por esse motivo, o processamento deve ser feito em menos de **60s**;
- Baseado *input* recebido, o sistema precisa regularmente gerar os **boletos** para cobrança e **disparar** mensagens para os e-mails ****da ****lista;
- E necessário configurar um arquivo docker-compose para rodar o projeto dentro de contêineres.

Esse arquivo *.csv* terá as seguintes colunas:

1. **name →** nome
2. **governmentId →** número do documento
3. **email →** email do sacado
4. **debtAmount →** valor
5. **debtDueDate →** Data para ser paga
6. **debtID →** uuid para o débito

Exemplo do conteúdo do arquivo:

```
name,governmentId,email,debtAmount,debtDueDate,debtId
John Doe,11111111111,johndoe@kanastra.com.br,1000000.00,2022-10-12,1adb6ccf-ff16-467f-bea7-5f05d494280f 
```

### Arquivo CSV do desafio

[input.csv](https://prod-files-secure.s3.us-west-2.amazonaws.com/59520267-1a82-407d-90da-7f3c8d88bf7d/782b942b-d6a0-4a54-b6f5-f015c74bb95f/input.csv)

### Informação importante:

1. **Projeto com Testes**
    - **Requisito Eliminatório**: O candidato deve entregar o projeto com testes abrangentes. Isso inclui:
        - **Testes Unitários**: Validação de componentes individuais do sistema.
        - **Testes de Integração**: Verificação do funcionamento conjunto de múltiplos componentes.
2. **Gestão de Boletos**
    - **Controle Rigoroso**: O projeto deve manter um controle eficiente dos boletos importados, gerados e enviados por e-mail. Este controle é crucial para garantir que:
        - **Evitar Duplicidades**: Mesmo se o mesmo arquivo for enviado novamente, o sistema não deve gerar ou enviar boletos duplicados.
        - **Processamento Parcial**: No caso de processamento parcial do arquivo (por exemplo, se apenas metade dos boletos foi processada na primeira tentativa), o sistema deve ser capaz de continuar de onde parou sem repetir operações já realizadas.
3. **Tratamento de Erros**
    - **Robustez do Sistema**: O sistema deve ser capaz de detectar e tratar erros durante o processo de geração e envio de boletos.
    - **Logs e Notificações**: Implementação de logs detalhados e notificações apropriadas para monitoramento e solução rápida de problemas.
4. **Documentação**
    - **Instruções de Uso**: Instruções detalhadas sobre como configurar, executar e testar o projeto no README.
5. **Boas Práticas de Programação**
    - **Código Limpo e Organizado**: Uso de boas práticas de programação para garantir que o código seja legível, sustentável e fácil de entender.
6. **Use de abstrações**
    - Não é necessário implementar um sistema real de envio de e-mails ou geração de boletos. O foco do teste é avaliar a estrutura e a lógica do código. Portanto, você pode usar classes abstratas para simular essas funcionalidades. Por exemplo:
    - **Classe de Geração de Boletos**: Crie uma classe que simule a geração de boletos. O método responsável pela geração de boletos pode simplesmente registrar uma mensagem no log, em vez de gerar um arquivo PDF real. O objetivo aqui é demonstrar a capacidade de estruturar a lógica necessária para a geração de boletos, sem a necessidade de uma implementação completa.
    - **Classe de Envio de E-mails**: De forma semelhante, crie uma classe que simule o envio de e-mails. O método de envio pode apenas registrar uma mensagem no log, indicando que o e-mail foi "enviado". Isso é suficiente para mostrar a compreensão do processo de envio de e-mails e a capacidade de integrar essa funcionalidade no sistema.
    
    A ideia principal é demonstrar a habilidade de criar a estrutura necessária para essas funcionalidades, focando na lógica e na integração com o restante do sistema, sem a necessidade de uma implementação real de geração de boletos ou envio de e-mails.
    
7. **Eficiência e Desempenho**
    - **Otimização**: O candidato deve demonstrar preocupação com a eficiência do código, buscando otimizar o desempenho sempre que possível.
    - **Escalabilidade**: A solução proposta deve ser escalável, capaz de lidar com um aumento no volume de boletos sem degradação significativa de desempenho.

# Pontos de atenção e lembretes

- Lembre-se dos princípios *S.O.L.I.D*;
- Lembre-se de Unit and integration tests (testes **no backend***,* testes sempre!);
- Lembre-se de *Error Handling*;
- Não será como uma prova de escola. Você poderá e provavelmente precisará consultar o google.