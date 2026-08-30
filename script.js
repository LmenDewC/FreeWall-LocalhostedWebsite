async function loadAnnouncements() {

    const container =
        document.getElementById("announcement-list");

    try {

        const response =
            await fetch("/api/announcements");

        if (!response.ok) {
            throw new Error("Server error");
        }

        const announcements =
            await response.json();

        container.innerHTML = "";

        if (announcements.length === 0) {

            container.innerHTML =
                "<p>No current announcements.</p>";

            return;
        }

        announcements.forEach(announcement => {

            const article =
                document.createElement("article");

            article.className = "announcement";

            const title =
                document.createElement("h3");

            title.textContent =
                announcement.title;

            const message =
                document.createElement("p");

            message.textContent =
                announcement.message;

            const expiration =
                document.createElement("small");

            const expiry =
                new Date(
                    announcement.expires
                );

            expiration.textContent =
                "Expires: " +
                expiry.toLocaleString();

            article.appendChild(title);
            article.appendChild(message);
            article.appendChild(expiration);

            container.appendChild(article);
        });

    } catch (error) {

        container.innerHTML =
            "<p>Unable to load announcements.</p>";

        console.error(error);
    }
}


// Load immediately
loadAnnouncements();


// Check for new announcements every 30 seconds
setInterval(
    loadAnnouncements,
    30000
);
