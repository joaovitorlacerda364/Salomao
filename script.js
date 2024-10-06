const API_URL = 'https://salomao.onrender.com/perguntar';
        const typingForm = document.querySelector(".typing-form");
        const chatContainer = document.querySelector(".chat-list");
        const suggestions = document.querySelectorAll(".suggestion");
        const toggleThemeButton = document.querySelector("#theme-toggle-button");
        const deleteChatButton = document.querySelector("#delete-chat-button");

        // Variável para manter o estado de resposta em andamento
        let userMessage = null;
        let isResponseGenerating = false;

        // Função para carregar dados de localStorage
        const loadDataFromLocalstorage = () => {
            const savedChats = localStorage.getItem("saved-chats");
            const isLightMode = localStorage.getItem("themeColor") === "light_mode";

            // Aplicar o tema armazenado
            document.body.classList.toggle("light_mode", isLightMode);
            toggleThemeButton.innerText = isLightMode ? "dark_mode" : "light_mode";

            // Restaurar chats salvos ou limpar o container de chats
            chatContainer.innerHTML = savedChats || "";
            document.body.classList.toggle("hide-header", savedChats);

            chatContainer.scrollTo(0, chatContainer.scrollHeight); // Rolagem automática até o final
        };

        // Função para criar uma nova mensagem
        const createMessageElement = (content, ...classes) => {
            const div = document.createElement("div");
            div.classList.add("message", ...classes);
            div.innerHTML = content;
            return div;
        };

        // Função para exibir animação de digitação
        const showTypingEffect = (text, textElement, incomingMessageDiv) => {
            const words = text.split(" ");
            let currentWordIndex = 0;

            const typingInterval = setInterval(() => {
                textElement.innerText +=
                    (currentWordIndex === 0 ? "" : " ") + words[currentWordIndex++];
                incomingMessageDiv.querySelector(".icon").classList.add("hide");

                if (currentWordIndex === words.length) {
                    clearInterval(typingInterval);
                    isResponseGenerating = false;
                    incomingMessageDiv.querySelector(".icon").classList.remove("hide");
                    localStorage.setItem("saved-chats", chatContainer.innerHTML); // Salvar histórico no localStorage
                }
                chatContainer.scrollTo(0, chatContainer.scrollHeight);
            }, 75);
        };

        // Função para gerar resposta da API
        const generateAPIResponse = async (incomingMessageDiv) => {
            const textElement = incomingMessageDiv.querySelector(".text");

            try {
                const response = await fetch(API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ pergunta: userMessage }),
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error.message);

                const apiResponse = data.resposta.replace(/\*\*(.*?)\*\*/g, "$1");
                showTypingEffect(apiResponse, textElement, incomingMessageDiv);
            } catch (error) {
                isResponseGenerating = false;
                textElement.innerText = error.message;
                textElement.parentElement.closest(".message").classList.add("error");
            } finally {
                incomingMessageDiv.classList.remove("loading");
            }
        };

        // Função para mostrar animação de carregamento
        const showLoadingAnimation = () => {
            const html = `<div class="message-content">
                            
                            <p class="text"></p>
                            <div class="loading-indicator">
                                <div class="loading-bar"></div>
                                <div class="loading-bar"></div>
                                <div class="loading-bar"></div>
                            </div>
                          </div>
                          <span onClick="copyMessage(this)" class="icon material-symbols-rounded">content_copy</span>`;

            const incomingMessageDiv = createMessageElement(html, "incoming", "loading");
            chatContainer.appendChild(incomingMessageDiv);

            chatContainer.scrollTo(0, chatContainer.scrollHeight);
            generateAPIResponse(incomingMessageDiv);
        };

        // Função para copiar mensagem
        const copyMessage = (copyButton) => {
            const messageText = copyButton.parentElement.querySelector(".text").innerText;

            navigator.clipboard.writeText(messageText);
            copyButton.innerText = "done";
            setTimeout(() => (copyButton.innerText = "content_copy"), 1000);
        };

        // Função para lidar com o envio de mensagens do chat
        const handleOutgoingChat = () => {
            userMessage = typingForm.querySelector(".typing-input").value.trim() || userMessage;
            if (!userMessage || isResponseGenerating) return;

            isResponseGenerating = true;

            const html = `<div class="message-content">
                           
                            <p class="text"></p>
                          </div>`;

            const outgoingMessageDiv = createMessageElement(html, "outgoing");
            outgoingMessageDiv.querySelector(".text").innerText = userMessage;
            chatContainer.appendChild(outgoingMessageDiv);

            typingForm.reset();
            document.body.classList.add("hide-header");
            chatContainer.scrollTo(0, chatContainer.scrollHeight);
            setTimeout(showLoadingAnimation, 500);
        };

        // Alternância entre temas claro e escuro
        toggleThemeButton.addEventListener("click", () => {
            const isLightMode = document.body.classList.toggle("light_mode");
            localStorage.setItem("themeColor", isLightMode ? "light_mode" : "dark_mode");
            toggleThemeButton.innerText = isLightMode ? "dark_mode" : "light_mode";
        });

        // Botão para deletar todas as conversas do localStorage
        deleteChatButton.addEventListener("click", () => {
            if (confirm("Are you sure you want to delete all the chats?")) {
                localStorage.removeItem("saved-chats");
                loadDataFromLocalstorage();
            }
        });

        // Definir mensagem do usuário e enviar chat ao clicar em uma sugestão
        suggestions.forEach((suggestion) => {
            suggestion.addEventListener("click", () => {
                userMessage = suggestion.querySelector(".text").innerText;
                handleOutgoingChat();
            });
        });

        // Prevenir submissão padrão do formulário e enviar chat
        typingForm.addEventListener("submit", (e) => {
            e.preventDefault();
            handleOutgoingChat();
        });

        // Carregar dados do localStorage ao carregar a página
        loadDataFromLocalstorage();