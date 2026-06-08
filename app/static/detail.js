function getPostIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("post_id");
}


async function loadPostDetail() {
    const postId = getPostIdFromUrl();
    const detailBox = document.getElementById("postDetail");

    if (!postId) {
        detailBox.innerHTML = "<p>게시글 ID가 없습니다.</p>";
        return;
    }

    const response = await fetch(`/posts/${postId}`);
    const post = await response.json();

    if (post.error) {
        detailBox.innerHTML = `<p>${post.error}</p>`;
        return;
    }

    detailBox.innerHTML = `
        <h2>${post.title}</h2>

        <p class="price">${Number(post.price).toLocaleString()}원</p>

        <div class="detail-info">
            <p><strong>카테고리:</strong> ${post.category}</p>
            <p><strong>거래 동네:</strong> ${post.dong}</p>
            <p><strong>조회수:</strong> ${Number(post.view_count).toLocaleString()}</p>
            <p><strong>관심 수:</strong> ${Number(post.like_count).toLocaleString()}</p>
            <p><strong>채팅 수:</strong> ${Number(post.chat_count).toLocaleString()}</p>
            <p><strong>등록일:</strong> ${post.created_at}</p>
        </div>

        <div class="description-box">
            <h3>게시글 설명</h3>
            <p>${post.description}</p>
        </div>
    `;
}


window.onload = loadPostDetail;