let currentTab = 'transcript';
let processingData = null;

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    document.getElementById(tabName).classList.add('active');
    document.querySelector(`button[onclick="showTab('${tabName}')"]`).classList.add('active');
    currentTab = tabName;

    if (processingData) {
        updateTabContent(tabName);
    }
}
function updateTabContent(tabName) {
    const contentDiv = document.getElementById(tabName);
    if (!contentDiv || !processingData) return;
    
    switch(tabName) {
        case 'transcript':
            contentDiv.innerHTML = `<p>${processingData.transcript || 'No transcript available'}</p>`;
            break;
        case 'summary':
            contentDiv.innerHTML = `<p>${processingData.summary || 'No summary available'}</p>`;
            break;
        case 'chapters':
            if (processingData.chapters && processingData.chapters.length > 0) {
                contentDiv.innerHTML = processingData.chapters.map(chapter => 
                    `<div class="chapter">
                        <h3>${chapter.title}</h3>
                        <p>${chapter.content}</p>
                    </div>`
                ).join('');
            } else {
                contentDiv.innerHTML = '<p>No chapters available</p>';
            }
            break;
        case 'notes':
            if (processingData.notes) {
                contentDiv.innerHTML = `<ul>${processingData.notes.map(note => 
                    `<li>${note}</li>`
                ).join('')}</ul>`;
            } else {
                contentDiv.innerHTML = '<p>No notes available</p>';
            }
            break;
        case 'flashcards':
            if (processingData.flashcards && processingData.flashcards.length > 0) {
                contentDiv.innerHTML = processingData.flashcards.map(card => 
                    `<div class="flashcard" onclick="this.classList.toggle('flipped')">
                        <div class="front">
                            <p>${card.question}</p>
                            <small>(Click to reveal answer)</small>
                        </div>
                        <div class="back">
                            <p>${card.answer}</p>
                        </div>
                    </div>`
                ).join('');
            } else {
                contentDiv.innerHTML = '<p>No flashcards available</p>';
            }
            break;
        case 'quiz':
            if (processingData.quiz && processingData.quiz.length > 0) {
                contentDiv.innerHTML = `
                    <div class="quiz-container">
                        ${processingData.quiz.map((q, i) => `
                            <div class="quiz-question" data-question="${i}">
                                <h3>Question ${i + 1}</h3>
                                <p>${q.question}</p>
                                <div class="quiz-options">
                                    ${q.options.map((opt, j) => `
                                        <div class="quiz-option" 
                                             data-option="${j}"
                                             onclick="selectOption(${i}, ${j})">
                                            ${['a', 'b', 'c', 'd'][j]}) ${opt}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('')}
                        <button class="quiz-submit" onclick="submitQuiz()">Submit Quiz</button>
                        <div class="quiz-score" style="display: none;"></div>
                    </div>
                `;
            } else {
                contentDiv.innerHTML = '<p>No quiz available</p>';
            }
            break;
    }
}
async function processVideo() {
    const videoUrl = document.getElementById('videoUrl').value;
    if (!videoUrl) {
        showError('Please enter a YouTube URL');
        return;
    }

    const loadingEl = document.getElementById('loading');
    const resultsEl = document.getElementById('results');
    const errorEl = document.getElementById('error-message');
    
    loadingEl.style.display = 'block';
    resultsEl.style.display = 'none';
    errorEl.style.display = 'none';

    try {
        console.log('Sending request to process video:', videoUrl); // Debug log
        
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: videoUrl })
        });

        const data = await response.json();
        console.log('Received response:', data); // Debug log

        if (!response.ok) {
            throw new Error(data.error || 'Failed to process video');
        }

        processingData = data;
        
        loadingEl.style.display = 'none';
        resultsEl.style.display = 'block';
        
        // Initialize with transcript tab
        currentTab = 'transcript';
        showTab('transcript');
    } catch (error) {
        console.error('Error processing video:', error); // Debug log
 
        resultsEl.style.display = 'none';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
}

function selectOption(questionIndex, optionIndex) {
    if (quizSubmitted) return;
    
    const questionDiv = document.querySelector(`[data-question="${questionIndex}"]`);
    const options = questionDiv.querySelectorAll('.quiz-option');
    
    options.forEach(opt => opt.classList.remove('selected'));
    options[optionIndex].classList.add('selected');
}

let quizSubmitted = false;

function submitQuiz() {
    if (quizSubmitted) return;
    
    const questions = document.querySelectorAll('.quiz-question');
    let score = 0;
    
    questions.forEach((q, i) => {
        const selectedOption = q.querySelector('.quiz-option.selected');
        if (!selectedOption) return;
        
        const selectedIndex = selectedOption.dataset.option;
        const correctIndex = ['a', 'b', 'c', 'd'].indexOf(processingData.quiz[i].correct.toLowerCase());
        
        if (parseInt(selectedIndex) === correctIndex) {
            score++;
            selectedOption.classList.add('correct');
        } else {
            selectedOption.classList.add('incorrect');
            q.querySelectorAll('.quiz-option')[correctIndex].classList.add('correct');
        }
    });
    
    const scoreDiv = document.querySelector('.quiz-score');
    scoreDiv.textContent = `Your Score: ${score}/${questions.length}`;
    scoreDiv.style.display = 'block';
    
    document.querySelector('.quiz-submit').disabled = true;
    quizSubmitted = true;
}