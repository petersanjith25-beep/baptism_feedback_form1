document.addEventListener('DOMContentLoaded', () => {
    // Select form controls
    const form = document.getElementById('feedbackForm');
    const formCard = document.getElementById('formCard');
    const successCard = document.getElementById('successCard');
    
    const nameInput = document.getElementById('name');
    const relationshipInput = document.getElementById('relationship');
    const invitationInput = document.getElementById('invitation_rating');
    const overallInput = document.getElementById('overall_rating');
    const foodInput = document.getElementById('food_rating');
    const improvementsInput = document.getElementById('improvements');
    const charNum = document.getElementById('charNum');
    
    // Select custom selectors containers
    const chipsContainer = document.getElementById('relationshipContainer');
    const invitationStarsContainer = document.getElementById('invitationRating');
    const overallStarsContainer = document.getElementById('overallRating');
    const foodContainer = document.getElementById('foodContainer');
    
    // Select Error Containers
    const nameError = document.getElementById('nameError');
    const relationshipError = document.getElementById('relationshipError');
    const invitationError = document.getElementById('invitationError');
    const overallError = document.getElementById('overallError');
    const foodError = document.getElementById('foodError');
    const apiErrorBox = document.getElementById('apiErrorBox');
    const apiErrorMessage = document.getElementById('apiErrorMessage');
    
    // Buttons
    const submitBtn = document.getElementById('submitBtn');
    const btnLoader = document.getElementById('btnLoader');
    const newResponseBtn = document.getElementById('newResponseBtn');

    // 1. Relationship Chips Selection
    chipsContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('.chip-btn');
        if (!btn) return;
        
        // Remove selection from others
        chipsContainer.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('selected'));
        
        // Select this one
        btn.classList.add('selected');
        relationshipInput.value = btn.dataset.value;
        
        // Clear error if active
        clearErrorState(relationshipInput, relationshipError);
    });

    // Helper for Star Ratings Setup
    function setupStarRating(container, hiddenInput, errorElement) {
        const stars = container.querySelectorAll('.star-btn');
        
        container.addEventListener('click', (e) => {
            const btn = e.target.closest('.star-btn');
            if (!btn) return;
            
            const ratingValue = parseInt(btn.dataset.value);
            hiddenInput.value = ratingValue;
            container.dataset.rating = ratingValue;
            
            // Mark active stars (class 'active' applied to stars <= selected value)
            stars.forEach(star => {
                const starVal = parseInt(star.dataset.value);
                if (starVal <= ratingValue) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });
            
            clearErrorState(hiddenInput, errorElement);
        });
    }

    // 2. Setup Star Ratings
    setupStarRating(invitationStarsContainer, invitationInput, invitationError);
    setupStarRating(overallStarsContainer, overallInput, overallError);

    // 3. Food Choice Selection
    foodContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.food-card');
        if (!card) return;
        
        // Remove selection from others
        foodContainer.querySelectorAll('.food-card').forEach(c => c.classList.remove('selected'));
        
        // Select this one
        card.classList.add('selected');
        foodInput.value = card.dataset.value;
        
        clearErrorState(foodInput, foodError);
    });

    // 4. Improvements Character Count
    improvementsInput.addEventListener('input', () => {
        const count = improvementsInput.value.length;
        charNum.textContent = count;
        
        if (count > 1000) {
            charNum.style.color = 'var(--error-color)';
        } else {
            charNum.style.color = 'var(--text-secondary)';
        }
    });

    // Helper to clear errors
    function clearErrorState(inputField, errorMsgElement) {
        const parent = inputField.closest('.form-group');
        if (parent) parent.classList.remove('has-error');
    }

    // Helper to show errors
    function setErrorState(inputField, errorMsgElement) {
        const parent = inputField.closest('.form-group');
        if (parent) parent.classList.add('has-error');
    }

    // 5. Client Side Validation
    function validateForm() {
        let isValid = true;

        // Name Validation
        if (!nameInput.value.trim()) {
            setErrorState(nameInput, nameError);
            isValid = false;
        } else {
            clearErrorState(nameInput, nameError);
        }

        // Relationship Validation
        if (!relationshipInput.value) {
            setErrorState(relationshipInput, relationshipError);
            isValid = false;
        } else {
            clearErrorState(relationshipInput, relationshipError);
        }

        // Invitation Rating Validation
        if (!invitationInput.value) {
            setErrorState(invitationInput, invitationError);
            isValid = false;
        } else {
            clearErrorState(invitationInput, invitationError);
        }

        // Overall Rating Validation
        if (!overallInput.value) {
            setErrorState(overallInput, overallError);
            isValid = false;
        } else {
            clearErrorState(overallInput, overallError);
        }

        // Food Rating Validation
        if (!foodInput.value) {
            setErrorState(foodInput, foodError);
            isValid = false;
        } else {
            clearErrorState(foodInput, foodError);
        }

        return isValid;
    }

    // Clear name error on typing
    nameInput.addEventListener('input', () => {
        if (nameInput.value.trim()) {
            clearErrorState(nameInput, nameError);
        }
    });

    // 6. Form Submission Handlers
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        apiErrorBox.style.display = 'none';

        if (!validateForm()) {
            // Scroll to the first error
            const firstError = document.querySelector('.form-group.has-error');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }

        // Set Loading State
        setSubmittingState(true);

        const formData = {
            name: nameInput.value.trim(),
            relationship: relationshipInput.value,
            invitation_rating: parseInt(invitationInput.value),
            overall_rating: parseInt(overallInput.value),
            food_rating: foodInput.value,
            improvements: improvementsInput.value.trim() || null
        };

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                // Smooth transition to Success Card
                formCard.style.display = 'none';
                successCard.style.display = 'block';
                successCard.scrollIntoView({ behavior: 'smooth' });
            } else {
                // Handle API error
                let errMsg = result.detail || 'Failed to submit feedback.';
                if (Array.isArray(result.detail)) {
                    // Extract validation messages from Pydantic errors if any
                    errMsg = result.detail.map(err => err.msg).join(', ');
                }
                showApiError(errMsg);
            }
        } catch (error) {
            console.error('Submission error:', error);
            showApiError('A network error occurred. Please check if the server is running and try again.');
        } finally {
            setSubmittingState(false);
        }
    });

    // Handle Submit Button States (Active/Loading)
    function setSubmittingState(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.querySelector('.btn-text').style.display = 'none';
            btnLoader.style.display = 'flex';
        } else {
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').style.display = 'block';
            btnLoader.style.display = 'none';
        }
    }

    // Show API Error
    function showApiError(msg) {
        apiErrorMessage.textContent = msg;
        apiErrorBox.style.display = 'block';
        apiErrorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // 7. Submit Another Response Reset Handler
    newResponseBtn.addEventListener('click', () => {
        // Reset inputs
        form.reset();
        
        relationshipInput.value = '';
        invitationInput.value = '';
        overallInput.value = '';
        foodInput.value = '';
        
        // Reset UI Components
        chipsContainer.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('selected'));
        
        invitationStarsContainer.querySelectorAll('.star-btn').forEach(s => s.classList.remove('active'));
        invitationStarsContainer.removeAttribute('data-rating');
        
        overallStarsContainer.querySelectorAll('.star-btn').forEach(s => s.classList.remove('active'));
        overallStarsContainer.removeAttribute('data-rating');
        
        foodContainer.querySelectorAll('.food-card').forEach(c => c.classList.remove('selected'));
        
        charNum.textContent = '0';
        charNum.style.color = 'var(--text-secondary)';
        
        // Remove error formatting classes
        document.querySelectorAll('.form-group').forEach(group => group.classList.remove('has-error'));
        
        // Hide API errors
        apiErrorBox.style.display = 'none';
        
        // Switch views
        successCard.style.display = 'none';
        formCard.style.display = 'block';
        formCard.scrollIntoView({ behavior: 'smooth' });
    });
});
