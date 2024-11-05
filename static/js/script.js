document.addEventListener('DOMContentLoaded', function() {
    console.log('Hello from JavaScript!');
});
 function submitWaterQuality() {
    // Simulate form submission and show results
    document.getElementById('results').innerHTML = `
        <div class="result-card">Your water is classified as ...</div>
        <button onclick="generateRecommendations()">Generate Recommendations</button>
    `;
}

function generateRecommendations() {
    // Simulate generating recommendations
    document.getElementById('results').innerHTML += `
        <div class="recommendations">
            <div class="recommendation-card">Method 1</div>
            <div class="recommendation-card">Method 2</div>
            <div class="recommendation-card">Method 3</div>
        </div>
    `;
}

function submitWaterQuality() {
    // Simulate form submission and show results
    document.getElementById('results').innerHTML = `
        <div class="result-card">Your water is classified as ...</div>
        <button onclick="generateRecommendations()">Generate Recommendations</button>
    `;
}

function generateRecommendations() {
    // Simulate generating recommendations
    document.getElementById('results').innerHTML += `
        <div class="recommendations">
            <div class="recommendation-card">Method 1</div>
            <div class="recommendation-card">Method 2</div>
            <div class="recommendation-card">Method 3</div>
        </div>
    `;
}

function showMethodDetails(method) {
    fetch('/method_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ method })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('results').innerHTML += `
            <div class="method-details">
                <h2>${data.method}</h2>
                <p>${data.description}</p>
                <p>Steps: ${data.steps}</p>
            </div>
        `;
    });
}

function generateRecommendations() {
    const category = document.querySelector('.result-card').innerText.split(' ')[4];

    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ category })
    })
    .then(response => response.json())
    .then(data => {
        let recommendationsHTML = '<div class="recommendations">';
        data.recommendations.forEach(rec => {
            recommendationsHTML += `<div class="recommendation-card" onclick="showMethodDetails('${rec}')">${rec}</div>`;
        });
        recommendationsHTML += '</div>';
        document.getElementById('results').innerHTML += recommendationsHTML;
    });
}

function submitWaterQuality() {
    const ph = document.getElementById('ph').value;
    const turbidity = document.getElementById('turbidity').value;
    const tds = document.getElementById('tds').value;

    fetch('/classify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ph, turbidity, tds })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('results').innerHTML = `
            <div class="result-card">Your water is classified as ${data.category}</div>
            <button onclick="generateRecommendations()">Generate Recommendations</button>
        `;
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    });
}

function generateRecommendations() {
    const category = document.querySelector('.result-card').innerText.split(' ')[4];

    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ category })
    })
    .then(response => response.json())
    .then(data => {
        let recommendationsHTML = '<div class="recommendations">';
        data.recommendations.forEach(rec => {
            recommendationsHTML += `<div class="recommendation-card" onclick="showMethodDetails('${rec}')">${rec}</div>`;
        });
        recommendationsHTML += '</div>';
        document.getElementById('results').innerHTML += recommendationsHTML;
        document.querySelector('.recommendations').scrollIntoView({ behavior: 'smooth' });
    });
}

function showMethodDetails(method) {
    fetch('/method_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ method })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('results').innerHTML += `
            <div class="method-details">
                <h2>${data.method}</h2>
                <p>${data.description}</p>
                <p>Steps: ${data.steps}</p>
            </div>
        `;
        document.querySelector('.method-details').scrollIntoView({ behavior: 'smooth' });
    });
}
