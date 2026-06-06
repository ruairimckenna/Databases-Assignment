function toggleMenu() {
    const dropdown = document.getElementById("dropdown");
    if (dropdown) {
        dropdown.classList.toggle("hidden");
    }
}

function toggleAnswer(cardId) {
    const answer = document.getElementById("answer-" + cardId);
    if (answer) {
        answer.classList.toggle("hidden");
    }
}

function filterFlashcards() {
    const filterInput = document.getElementById("table-filter");
    const topicFilterSelect = document.getElementById("topic-filter");
    const subtopicFilterSelect = document.getElementById("subtopic-filter");
    
    const filter = filterInput ? filterInput.value.toLowerCase() : "";
    const topicFilterValue = topicFilterSelect ? topicFilterSelect.value : "all";
    const subtopicFilterValue = subtopicFilterSelect ? subtopicFilterSelect.value : "all";
    
    let topicFilterText = null;
    if (topicFilterSelect && topicFilterValue !== "all") {
        const selectedIndex = topicFilterSelect.selectedIndex;
        if (selectedIndex >= 0) {
            topicFilterText = topicFilterSelect.options[selectedIndex].textContent.toLowerCase();
        }
    }

    const rows = document.querySelectorAll("#flashcard-table tbody tr");
    rows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        const topicCell = row.cells[0];
        const subtopicCell = row.cells[1];
        
        const topicText = topicCell ? topicCell.textContent.toLowerCase() : "";
        const subtopicText = subtopicCell ? subtopicCell.textContent.toLowerCase() : "";
        
        const topicMatch = topicFilterValue === "all" || topicText === topicFilterText;
        const subtopicMatch = subtopicFilterValue === "all" || subtopicText === subtopicFilterValue;
        
        const shouldShow = topicMatch && subtopicMatch && text.includes(filter);
        row.style.display = shouldShow ? "" : "none";
    });
}

let studyCardIndex = 0;
let studyCardCount = 0;
let studyFilteredIndexes = [];

function initStudyGallery(count) {
    studyCardCount = count;
    studyFilteredIndexes = [];
    for (let i = 0; i < count; i++) {
        studyFilteredIndexes.push(i);
    }
    studyCardIndex = 0;
    showStudyCard(studyCardIndex);
}

function showStudyCard(index) {
    const cards = document.querySelectorAll('.study-card-item');
    if (!cards || cards.length === 0) return;
    
    var visibleIndexes = [];
    if (studyFilteredIndexes.length > 0) {
        visibleIndexes = studyFilteredIndexes;
    } else {
        for (var i = 0; i < cards.length; i++) {
            visibleIndexes.push(i);
        }
    }
    
    if (!visibleIndexes || visibleIndexes.length === 0) return;
    
    var normalizedIndex = ((index % visibleIndexes.length) + visibleIndexes.length) % visibleIndexes.length;
    var actualIndex = visibleIndexes[normalizedIndex];
    
    cards.forEach(function(card, idx) {
        if (idx === actualIndex) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
    
    const position = document.getElementById('study-card-position');
    if (position) {
        position.textContent = (normalizedIndex + 1) + " / " + visibleIndexes.length;
    }
}

function changeStudyCard(delta) {
    var visibleCount = studyFilteredIndexes.length > 0 ? studyFilteredIndexes.length : studyCardCount;
    if (!visibleCount) return;
    studyCardIndex = (studyCardIndex + delta + visibleCount) % visibleCount;
    showStudyCard(studyCardIndex);
}

function filterStudyCards() {
    const searchInput = document.getElementById('study-search');
    const subtopicSelect = document.getElementById('study-subtopic-filter');
    
    const query = searchInput ? searchInput.value.toLowerCase() : '';
    const subtopicValue = subtopicSelect ? subtopicSelect.value : 'all';
    
    const cards = document.querySelectorAll('.study-card-item');
    studyFilteredIndexes = [];
    
    cards.forEach(function(card, idx) {
        const text = card.dataset.search ? card.dataset.search : '';
        const subtopic = card.dataset.subtopic ? card.dataset.subtopic : '';
        
        const matchesSubtopic = subtopicValue === 'all' || subtopic === subtopicValue;
        const matchesSearch = !query || text.includes(query);
        const visible = matchesSubtopic && matchesSearch;
        
        if (visible) {
            card.classList.remove('hidden');
            studyFilteredIndexes.push(idx);
        } else {
            card.classList.add('hidden');
        }
    });

    const noResults = document.getElementById('study-no-results');
    if (studyFilteredIndexes.length === 0) {
        if (noResults) {
            noResults.classList.remove('hidden');
        }
        const position = document.getElementById('study-card-position');
        if (position) {
            position.textContent = '0 / 0';
        }
        return;
    }

    if (noResults) {
        noResults.classList.add('hidden');
    }
    studyCardIndex = 0;
    showStudyCard(studyCardIndex);
}
