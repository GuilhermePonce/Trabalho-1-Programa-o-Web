# Meeting Planner

Sistema Web em Python + Django para gerenciamento de reuniões entre gerentes e funcionários. 
O projeto foi pensado para atender ao trabalho da disciplina INF1407

# Componentes do grupo

- Guilherme Ponce 2011179

# Executar localmente
Instale as dependências:
python -m pip install -r requirements.txt

Aplique as migrações:
python manage.py migrate

Crie os dados de demonstração:
Foi criado para facilitar os testes do sistema, credenciais estão a seguir no readme
python manage.py seed_demo

Inicie o servidor:
python manage.py runserver

Acesse no navegador:
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/

# Provedor web

https://trabalho-1-programa-o-web.onrender.com

# Escopo do site

O site permite que um usuário com perfil de gerente cadastre funcionários, agende reuniões e acompanhe as respostas dos convites. 
Já o usuário com perfil de funcionário consegue entrar no sistema, visualizar os convites recebidos e responder se vai participar ou não.

Perfis disponíveis:

- Gerente: cadastra, consulta, altera e remove funcionários do seu time. Também cria, visualiza, atualiza e exclui reuniões.

- Funcionário: acessa apenas os seus convites e responde cada reunião com status de aceite ou recusa.

- Admin: possui acesso completo ao Django Admin e também pode visualizar o sistema como qualquer membro usando os links Ver como, esse usuário foi criado para facilitar testes e visualizações do projeto.

# Usuários de teste

Login e senha

admin / admin12345
gerente_demo / gerente12345
funcionario_demo1 / func12345
funcionario_demo2 / func12345

# Fluxo gerente
O gerente possui as opções de :
Visualizar
Editar
Criar
Através dos botões correspondentes permitindo cada ação, ele é responsável por editar seus funionários no painel e de marcar suas reuniões, também editáveis no painel.


# Fluxo funcionário
O funcionário possui as opções de:
Visualizar
Responder convite
Através dos botões correspondentes o funcionário pode através do painel aceitar ou recusar uma reunião.

# Fluxo Admin
O usuário Admin foi criado apenas para facilitar testes, onde é possível mudar papéis sem precisar fazer login e logout e é possível visualizar como papel de gerente ou funcionário.
Para utiliza-lo é só logar como admin e realizar as ações correspondentes no painel.

# Funcionalidades implementadas

- Login e logout com autenticação do Django.
- Visões diferentes para gerente e funcionário.
- CRUD de funcionários.
- CRUD de reuniões.
- Resposta de convites de reunião por funcionários.
- Área administrativa do Django.
- Usuário administrador de teste com todas as permissões.
- Dados de demonstração gerados por comando.

# O que foi testado e funcionou

- Login com gerente, funcionário e admin.
- CRUD de funcionários pelo gerente.
- CRUD de reuniões pelo gerente.
- Resposta de convite pelo funcionário.
- Redirecionamento do funcionário para a área correta.
- Visualização do sistema pelo usuário admin.
- Testes automatizados básicos com python manage.py test.


# O que não funcionou
- No render não foi possível estiliazar com css