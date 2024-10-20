// Define the initial message
const initialMessage = "Ready to conquer Europe? Let's make sure your startup is too!";

// Define the questions
const questions = [
    "What types of personal data does your SaaS collect, and how is this data processed and stored? Please include details about the data subjects, the purpose of data collection, and any third-party data processors involved.",
    "Does your SaaS utilize any AI or machine learning algorithms, particularly in automated decision-making processes? If so, please describe these AI systems, their decision-making processes, and how their outputs are used.",
    "How does your SaaS handle user consent, and what mechanisms are in place to facilitate the exercise of data subject rights (such as access, rectification, deletion, and data portability) under GDPR?",
    "What security measures does your SaaS implement to protect personal data, and what is your procedure for handling data breaches, including notification to authorities and affected data subjects?",
    "What measures have you taken to ensure compliance with relevant regulatory frameworks, including GDPR and the AI Act? Please detail any audits, certifications, or legal reviews that have been conducted.",
    "Is there any other information regarding your SaaS's operations, data processing activities, or AI systems that you believe is relevant for assessing compliance with GDPR and the AI Act?"
];

let currentQuestionIndex = 0;

// Array to store user's responses
let userResponses = [];

// Select the HTML elements for chat and user input
const chatBox = document.getElementById('chat-messages');
const userInput = document.getElementById('user-message');
const sendBtn = document.getElementById('send-btn');

// Function to add a message to the chat (either from the user or the bot)
function appendMessage(sender, text) {
    const messageElem = document.createElement('div');
    messageElem.classList.add('message');

    // Add specific class based on the sender (user or bot)
    if (sender === 'user') {
        messageElem.classList.add('user-message');
    } else {
        messageElem.classList.add('bot-message');
    }

    messageElem.textContent = text;
    chatBox.appendChild(messageElem);
    chatBox.scrollTop = chatBox.scrollHeight; // Automatically scroll to the bottom of the chat
}

// Function to show the next question in the sequence
function showNextMessage() {
    if (currentQuestionIndex < questions.length) {
        appendMessage('bot', questions[currentQuestionIndex]); // Display the next question
        currentQuestionIndex++;
    } else {
        // Once all questions are answered, send the responses to the server
        sendData(userResponses); // Send responses to the backend
    }
}

// Function to send user's responses to the backend
function sendData(answers) {
    fetch('http://127.0.0.1:5000/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            answer0: answers[0],
            answer1: answers[1],
            answer2: answers[2],
            answer3: answers[3],
            answer4: answers[4],
            answer5: answers[5]
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        // Gestisci i dati ricevuti dal server
        // Mostra la risposta del backend nella chat
        appendMessage('bot', "GDPR Responses:");
        data.GDPR.forEach(response => {
            appendMessage('bot', `Domanda: ${response.domanda}, Voto: ${response.voto}, Risposta: ${response.risposta}`);
        });

        appendMessage('bot', "AIACT Responses:");
        data.AIACT.forEach(response => {
            appendMessage('bot', `Domanda: ${response.domanda}, Voto: ${response.voto}, Risposta: ${response.risposta}`);
        });
    })
    .catch((error) => {
        console.error('Error:', error);
        appendMessage('bot', 'Si è verificato un errore nel ricevere la risposta.');
    });
}


// Function to handle user's input and send the message
function sendMessage() {
    const userText = userInput.value.trim();
    if (userText !== "") {
        appendMessage('user', userText); // Display the user's message in the chat
        userInput.value = ''; // Clear the input field

        // Save the user's response
        userResponses.push(userText);

        // If all 6 responses have been collected, send the data to the server
        if (userResponses.length === 6) {
            sendData(userResponses); // Send the responses to the server
        } else {
            // If not all questions have been answered, show the next question
            setTimeout(showNextMessage, 1000); // Wait 1 second before showing the next question
        }
    }
}

// Event listener for the Send button
sendBtn.addEventListener('click', sendMessage);

// Allow sending the message by pressing "Enter"
userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage(); // Send the message if the Enter key is pressed
    }
});

// Start the conversation when the page loads
window.onload = function() {
    // Show the initial message after 1 second
    setTimeout(function() {
        appendMessage('bot', initialMessage);

        // Show the first question after another 1 second
        setTimeout(function() {
            showNextMessage();
        }, 1000);
    }, 1000);
};
