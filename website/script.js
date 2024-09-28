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

// Select the HTML elements
const chatBox = document.getElementById('chat-messages');
const userInput = document.getElementById('user-message');
const sendBtn = document.getElementById('send-btn');

// Function to add a message to the chat
function appendMessage(sender, text) {
    const messageElem = document.createElement('div');
    messageElem.classList.add('message');

    // Add specific class based on the sender
    if (sender === 'user') {
        messageElem.classList.add('user-message');
    } else {
        messageElem.classList.add('bot-message');
    }

    messageElem.textContent = text;
    chatBox.appendChild(messageElem);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to show the next question
function showNextMessage() {
    if (currentQuestionIndex < questions.length) {
        appendMessage('bot', questions[currentQuestionIndex]);
        currentQuestionIndex++;
    } else {
        appendMessage('bot', "Thanks for your responses! We'll be in touch soon.");
        userInput.disabled = true;
        sendBtn.disabled = true;

        // Here you can handle the collected responses, e.g., send them to a server
        console.log("User Responses:", userResponses);
        // Example: sendResponsesToServer(userResponses);
    }
}

// Function to handle user's message
function sendMessage() {
    const userText = userInput.value.trim();
    if (userText !== "") {
        appendMessage('user', userText);
        userInput.value = '';

        // Save the user's response
        userResponses.push(userText);

        setTimeout(showNextMessage, 1000);
    }
}

// Event listener for the Send button
sendBtn.addEventListener('click', sendMessage);

// Allow sending message by pressing "Enter"
userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Start the conversation
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
