async function loadUsers() {
    const response = await fetch("/users");
    const data = await response.json();

    const userSelect = document.getElementById("userSelect");
    userSelect.innerHTML = "";

    data.users.forEach(userId => {
        const option = document.createElement("option");
        option.value = userId;
        option.textContent = userId;
        userSelect.appendChild(option);
    });

    if (data.users.length > 0) {
        userSelect.value = data.users[0];
        loadRecommendations();
    }
}

async function loadUserPreference(userId) {
    const response = await fetch(`/user-preferences/${userId}`);
    const data = await response.json();

    const preferenceBox = document.getElementById("userPreference");

    if (data.error) {
        preferenceBox.innerHTML = `<p>${data.error}</p>`;
        return;
    }

    preferenceBox.innerHTML = `
        <h3>${userId} 선호 정보</h3>
        <p>선호 카테고리: ${data.preferred_category_1}, ${data.preferred_category_2}</p>
        <p>선호 동네: ${data.preferred_dong}</p>
        <p>선호 가격대: ${Number(data.min_price).toLocaleString()}원 ~ ${Number(data.max_price).toLocaleString()}원</p>
    `;
}

async function loadRecommendations() {
    const userId = document.getElementById("userSelect").value;
    const topN = document.getElementById("topN").value;

    await loadUserPreference(userId);

    const response = await fetch(`/recommend/hybrid/${userId}?top_n=${topN}`);
    const data = await response.json();

    const list = document.getElementById("recommendationList");
    list.innerHTML = "";

    if (!data.recommendations || data.recommendations.length === 0) {
        list.innerHTML = "<p>추천 결과가 없습니다.</p>";
        return;
    }

    data.recommendations.forEach(post => {
        const card = document.createElement("div");
        card.className = "card";

        card.innerHTML = `
            <h3>${post.title}</h3>
            <p class="meta">카테고리: ${post.category}</p>
            <p class="meta">동네: ${post.dong}</p>
            <p class="price">${Number(post.price).toLocaleString()}원</p>
            <p class="score">추천 점수: ${Number(post.hybrid_score).toFixed(4)}</p>
        `;

        list.appendChild(card);
    });
}

window.onload = loadUsers;