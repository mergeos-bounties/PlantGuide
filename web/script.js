document.addEventListener('DOMContentLoaded', function() {
    // Sample plant traits/tags
    const plantTraits = [
        'Leaves', 'Flowers', 'Fruit', 'Bark', 'Roots',
        'Height', 'Spread', 'Sunlight', 'Water', 'Soil'
    ];

    // Sample care information for demonstration
    const careInfo = {
        'Leaves': {
            title: 'Leaf Care',
            description: 'Ensure your plant gets enough light for healthy leaf growth.',
            tips: 'Rotate the plant regularly for even growth.'
        },
        'Flowers': {
            title: 'Flower Care',
            description: 'Provide the right conditions for your plant to produce beautiful flowers.',
            tips: 'Fertilize regularly to encourage blooming.'
        },
        // Add more care information as needed
    };

    const tagsContainer = document.querySelector('.tags');
    const careCard = document.getElementById('care-card');

    // Create tag elements
    plantTraits.forEach(trait => {
        const tagElement = document.createElement('div');
        tagElement.className = 'tag';
        tagElement.textContent = trait;
        tagElement.addEventListener('click', () => toggleTag(tagElement, trait));
        tagsContainer.appendChild(tagElement);
    });

    function toggleTag(tagElement, trait) {
        tagElement.classList.toggle('selected');

        // Update care card based on selected tags
        updateCareCard();
    }

    function updateCareCard() {
        const selectedTags = document.querySelectorAll('.tag.selected');
        careCard.innerHTML = '';

        if (selectedTags.length === 0) {
            careCard.innerHTML = '<p>Select plant traits to see care information.</p>';
            return;
        }

        selectedTags.forEach(tag => {
            const trait = tag.textContent;
            if (careInfo[trait]) {
                const cardSection = document.createElement('div');
                cardSection.innerHTML = `
                    <h3>${careInfo[trait].title}</h3>
                    <p>${careInfo[trait].description}</p>
                    <p><strong>Tip:</strong> ${careInfo[trait].tips}</p>
                `;
                careCard.appendChild(cardSection);
            }
        });
    }
});