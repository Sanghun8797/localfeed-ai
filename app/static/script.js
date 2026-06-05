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
        await loadSelectedUserPreference();
        await loadRecommendations();
    }
}


async function loadSelectedUserPreference() {
    const userId = document.getElementById("userSelect").value;

    const response = await fetch(`/user-preferences/${userId}`);
    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    document.getElementById("category1").value = data.preferred_category_1;
    document.getElementById("category2").value = data.preferred_category_2;
    document.getElementById("dong").value = data.preferred_dong;
    document.getElementById("minPrice").value = data.min_price;
    document.getElementById("maxPrice").value = data.max_price;

    updatePreferenceBox();
}


function updatePreferenceBox() {
    const userId = document.getElementById("userSelect").value;
    const category1 = document.getElementById("category1").value;
    const category2 = document.getElementById("category2").value;
    const dong = document.getElementById("dong").value;
    const minPrice = document.getElementById("minPrice").value;
    const maxPrice = document.getElementById("maxPrice").value;

    const preferenceBox = document.getElementById("userPreference");

    preferenceBox.innerHTML = `
        <h3>${userId} 기반 추천 조건</h3>
        <p>선호 카테고리: ${category1}, ${category2}</p>
        <p>선호 동네: ${dong}</p>
        <p>선호 가격대: ${Number(minPrice).toLocaleString()}원 ~ ${Number(maxPrice).toLocaleString()}원</p>
        <p class="meta">샘플 사용자의 기본 선호 정보를 불러온 뒤, 현재 입력된 조건을 기준으로 추천합니다.</p>
    `;
}


async function loadRecommendations() {
    const category1 = document.getElementById("category1").value;
    const category2 = document.getElementById("category2").value;
    const dong = document.getElementById("dong").value;
    const minPrice = document.getElementById("minPrice").value;
    const maxPrice = document.getElementById("maxPrice").value;
    const topN = document.getElementById("topN").value;

    if (Number(minPrice) > Number(maxPrice)) {
        alert("최소 가격은 최대 가격보다 클 수 없습니다.");
        return;
    }

    updatePreferenceBox();

    const url = `/recommend/custom?category1=${encodeURIComponent(category1)}&category2=${encodeURIComponent(category2)}&dong=${encodeURIComponent(dong)}&min_price=${minPrice}&max_price=${maxPrice}&top_n=${topN}`;

    const response = await fetch(url);
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