function toggleMenu() {
    const dropdown = document.getElementById("dropdown");
    dropdown.classList.toggle("hidden");
}

function toggleAnswer(cardId) {
    const answer = document.getElementById("answer-" + cardId);
    if (answer) {
        answer.classList.toggle("hidden");
    }
}
