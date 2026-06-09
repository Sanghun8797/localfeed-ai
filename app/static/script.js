function updatePreferenceBox() {
    const userName = document.getElementById("userName").value.trim();
    const category1 = document.getElementById("category1").value;
    const category2 = document.getElementById("category2").value;
    const dong = document.getElementById("dong").value;
    const minPrice = document.getElementById("minPrice").value;
    const maxPrice = document.getElementById("maxPrice").value;

    const preferenceBox = document.getElementById("userPreference");

    preferenceBox.style.display = "block";

    preferenceBox.innerHTML = `
        <h3>${userName}님을 위한 추천 조건</h3>
        <p>추천 방식: 선호 조건 기반 AI 추천</p>
        <p>선호 카테고리: ${category1}, ${category2}</p>
        <p>선호 동네: ${dong}</p>
        <p>선호 가격대: ${Number(minPrice).toLocaleString()}원 ~ ${Number(maxPrice).toLocaleString()}원</p>
        <p class="meta">입력한 선호 조건을 기준으로 카테고리, 동네, 가격대, 인기도, 최신성을 반영해 추천합니다.</p>
    `;
}


function getScoreLabel(score100) {
    if (score100 >= 85) return "매우 높음";
    if (score100 >= 70) return "높음";
    if (score100 >= 50) return "보통";
    return "낮음";
}


async function loadRecommendations() {
    const userName = document.getElementById("userName").value.trim();

    if (!userName) {
        alert("사용자 이름을 입력해주세요.");
        return;
    }

    const category1 = document.getElementById("category1").value;
    const category2 = document.getElementById("category2").value;
    const dong = document.getElementById("dong").value;
    const minPrice = document.getElementById("minPrice").value;
    const maxPrice = document.getElementById("maxPrice").value;
    const topN = document.getElementById("topN").value;

    if (!category1) {
        alert("선호 카테고리 1을 선택해주세요.");
        return;
    }

    if (!category2) {
        alert("선호 카테고리 2를 선택해주세요.");
        return;
    }

    if (!dong) {
        alert("선호 동네를 선택해주세요.");
        return;
    }

    if (category1 === category2) {
        alert("선호 카테고리 1과 선호 카테고리 2는 서로 다르게 선택해야 합니다.");
        return;
    }

    if (Number(minPrice) < 0 || Number(maxPrice) < 0) {
        alert("가격은 0원 이상으로 입력해주세요.");
        return;
    }

    if (Number(maxPrice) === 0) {
        alert("최대 가격을 0원보다 크게 입력해주세요.");
        return;
    }

    if (Number(minPrice) > Number(maxPrice)) {
        alert("최소 가격은 최대 가격보다 클 수 없습니다.");
        return;
    }

    updatePreferenceBox();

    const recommendationSection = document.getElementById("recommendationSection");
    recommendationSection.style.display = "block";

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

        card.onclick = () => {
            window.location.href = `/static/detail.html?post_id=${post.post_id}`;
        };

        const score = Number(post.hybrid_score);
        const score100 = Math.round(score * 100);
        const scoreLabel = getScoreLabel(score100);

        card.innerHTML = `
            <h3>${post.title}</h3>
            <p class="meta">카테고리: ${post.category}</p>
            <p class="meta">동네: ${post.dong}</p>
            <p class="price">${Number(post.price).toLocaleString()}원</p>
            <p class="score">추천 적합도: ${scoreLabel}</p>
            <p class="score">추천 점수: ${score100}점 / 100점</p>
        `;

        list.appendChild(card);
    });
}