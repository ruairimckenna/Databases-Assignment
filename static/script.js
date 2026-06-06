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

function filterFlashcards() {
    const filter = document.getElementById("table-filter")?.value.toLowerCase() || "";
    const topicFilterSelect = document.getElementById("topic-filter");
    const subtopicFilterSelect = document.getElementById("subtopic-filter");
    const topicFilterValue = topicFilterSelect?.value || "all";
    const topicFilterText = topicFilterSelect && topicFilterValue !== "all"
        ? topicFilterSelect.options[topicFilterSelect.selectedIndex].textContent.toLowerCase()
        : null;
    const subtopicFilterValue = subtopicFilterSelect?.value || "all";

    const rows = document.querySelectorAll("#flashcard-table tbody tr");
    rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        const topicText = row.cells[0]?.textContent.toLowerCase() || "";
        const subtopicText = row.cells[1]?.textContent.toLowerCase() || "";
        const topicMatch = topicFilterValue === "all" || topicText === topicFilterText;
        const subtopicMatch = subtopicFilterValue === "all" || subtopicText === subtopicFilterValue;
        row.style.display = topicMatch && subtopicMatch && text.includes(filter) ? "" : "none";
    });
}

let studyCardIndex = 0;
let studyCardCount = 0;
let studyFilteredIndexes = [];

function initStudyGallery(count) {
    studyCardCount = count;
    studyFilteredIndexes = Array.from({ length: count }, (_, idx) => idx);
    studyCardIndex = 0;
    showStudyCard(studyCardIndex);
}

function showStudyCard(index) {
    const cards = document.querySelectorAll('.study-card-item');
    if (!cards.length) return;
    const visibleIndexes = studyFilteredIndexes.length ? studyFilteredIndexes : Array.from(cards.keys());
    if (!visibleIndexes.length) return;
    const normalizedIndex = ((index % visibleIndexes.length) + visibleIndexes.length) % visibleIndexes.length;
    const actualIndex = visibleIndexes[normalizedIndex];
    cards.forEach((card, idx) => {
        card.classList.toggle('hidden', idx !== actualIndex);
    });
    const position = document.getElementById('study-card-position');
    if (position) {
        position.textContent = `${normalizedIndex + 1} / ${visibleIndexes.length}`;
    }
}

function changeStudyCard(delta) {
    const visibleCount = studyFilteredIndexes.length ? studyFilteredIndexes.length : studyCardCount;
    if (!visibleCount) return;
    studyCardIndex = (studyCardIndex + delta + visibleCount) % visibleCount;
    showStudyCard(studyCardIndex);
}

function filterStudyCards() {
    const query = document.getElementById('study-search')?.value.toLowerCase() || '';
    const subtopicValue = document.getElementById('study-subtopic-filter')?.value || 'all';
    const cards = document.querySelectorAll('.study-card-item');
    studyFilteredIndexes = [];
    cards.forEach((card, idx) => {
        const text = card.dataset.search || '';
        const subtopic = card.dataset.subtopic || '';
        const matchesSubtopic = subtopicValue === 'all' || subtopic === subtopicValue;
        const matchesSearch = !query || text.includes(query);
        const visible = matchesSubtopic && matchesSearch;
        card.classList.toggle('hidden', !visible);
        if (visible) {
            studyFilteredIndexes.push(idx);
        }
    });

    const noResults = document.getElementById('study-no-results');
    if (studyFilteredIndexes.length === 0) {
        noResults?.classList.remove('hidden');
        document.getElementById('study-card-position')?.textContent = '0 / 0';
        return;
    }

    noResults?.classList.add('hidden');
    studyCardIndex = 0;
    showStudyCard(studyCardIndex);
}
