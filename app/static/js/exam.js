document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const questionContainer = document.getElementById('question-container');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const markForReviewBtn = document.getElementById('mark-for-review');
    const questionNavigation = document.getElementById('question-navigation');
    const timerDisplay = document.getElementById('timer');
    const submitBtn = document.getElementById('submit-exam');

    // Exam State
    let currentQuestionIndex = 0;
    const userAnswers = {}; // { questionId: answer }
    const questionStatus = Array(examData.questions.length).fill('unanswered'); // unanswered, answered, marked

    function startTimer(durationMinutes) {
        let totalSeconds = durationMinutes * 60;

        const timerInterval = setInterval(() => {
            if (totalSeconds <= 0) {
                clearInterval(timerInterval);
                alert("Time's up! The exam will now be submitted.");
                // In a real app, you would trigger the submit function here.
                submitBtn.click();
                return;
            }

            totalSeconds--;

            const hours = Math.floor(totalSeconds / 3600);
            const minutes = Math.floor((totalSeconds % 3600) / 60);
            const seconds = totalSeconds % 60;

            document.getElementById('hours').textContent = String(hours).padStart(2, '0');
            document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
            document.getElementById('seconds').textContent = String(seconds).padStart(2, '0');
        }, 1000);
    }

    function renderQuestion(index) {
        const question = examData.questions[index];
        let optionsHtml = '';

        if (question.type === 'mcq_single' || question.type === 'mcq_multiple') {
            const inputType = question.type === 'mcq_single' ? 'radio' : 'checkbox';
            optionsHtml = question.options.map((option, i) => `
                <div class="option">
                    <input type="${inputType}" name="option" value="${i}" id="option${i}">
                    <label for="option${i}">${option}</label>
                </div>
            `).join('');
        } else if (question.type === 'short_answer') {
            optionsHtml = `
                <div class="option">
                    <input type="text" class="short-answer-input" placeholder="Enter your answer">
                </div>
            `;
        }

        questionContainer.innerHTML = `
            <h3>Question ${index + 1} of ${examData.questions.length}</h3>
            <p>${question.text}</p>
            <div class="options-container">
                ${optionsHtml}
            </div>
        `;
        updateNavigation();
    }

    function updateNavigation() {
        // This function will update the colors of the navigation buttons
        // based on the questionStatus array.
        const navButtons = questionNavigation.querySelectorAll('.nav-button');
        navButtons.forEach((btn, i) => {
            btn.classList.remove('current', 'answered', 'marked');
            if (i === currentQuestionIndex) {
                btn.classList.add('current');
            }
            if (questionStatus[i] === 'answered') {
                btn.classList.add('answered');
            } else if (questionStatus[i] === 'marked') {
                btn.classList.add('marked');
            }
        });
    }

    function saveAnswer() {
        const question = examData.questions[currentQuestionIndex];
        const questionId = question.id;
        let answer = null;

        if (question.type === 'mcq_single') {
            const selectedOption = questionContainer.querySelector('input[name="option"]:checked');
            if (selectedOption) {
                answer = selectedOption.value;
                questionStatus[currentQuestionIndex] = 'answered';
            }
        } else if (question.type === 'mcq_multiple') {
            const selectedOptions = Array.from(questionContainer.querySelectorAll('input[name="option"]:checked'));
            answer = selectedOptions.map(input => input.value);
            if (answer.length > 0) {
                questionStatus[currentQuestionIndex] = 'answered';
            }
        } else if (question.type === 'short_answer') {
            const input = questionContainer.querySelector('.short-answer-input');
            answer = input.value.trim();
            if (answer !== '') {
                questionStatus[currentQuestionIndex] = 'answered';
            }
        }

        userAnswers[questionId] = answer;
    }

    // Event Listeners
    markForReviewBtn.addEventListener('click', () => {
        // Toggle 'marked' status, but only if it's not already answered
        if (questionStatus[currentQuestionIndex] !== 'answered') {
            questionStatus[currentQuestionIndex] = questionStatus[currentQuestionIndex] === 'marked' ? 'unanswered' : 'marked';
            updateNavigation();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentQuestionIndex < examData.questions.length - 1) {
            saveAnswer();
            currentQuestionIndex++;
            renderQuestion(currentQuestionIndex);
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentQuestionIndex > 0) {
            saveAnswer();
            currentQuestionIndex--;
            renderQuestion(currentQuestionIndex);
        }
    });

    questionNavigation.addEventListener('click', (e) => {
        if (e.target.matches('.nav-button')) {
            saveAnswer();
            const index = parseInt(e.target.dataset.questionIndex, 10);
            currentQuestionIndex = index;
            renderQuestion(currentQuestionIndex);
        }
    });

    // Initial Load
    renderQuestion(currentQuestionIndex);
    startTimer(examData.duration_minutes);
});