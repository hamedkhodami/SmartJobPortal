document.addEventListener("DOMContentLoaded", () => {
  const mobileBtn = document.getElementById("mobileMenuButton");
  const mobileMenu = document.getElementById("mobileMenu");
  const profileBtn = document.getElementById("profileToggle");
  const profileMenu = document.getElementById("profileDropdownMenu");

  mobileBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });

  profileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    profileMenu.classList.toggle("hidden");
  });

  document.addEventListener("click", (e) => {
    if (!profileMenu.classList.contains("hidden")) {
      profileMenu.classList.add("hidden");
    }
  });
});


document.addEventListener("DOMContentLoaded", () => {
  const resumeInput = document.getElementById("resume");

  resumeInput.addEventListener("change", () => {
    const fileName = resumeInput.files[0]?.name || "";
    if (fileName) {
      resumeInput.setAttribute("title", fileName);
    }
  });
});


document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".counter");

  counters.forEach(counter => {
    const target = +counter.dataset.count;
    let count = 0;

    const update = () => {
      count += Math.max(1, Math.floor(target / 30));
      if (count >= target) {
        counter.textContent = target;
      } else {
        counter.textContent = count;
        requestAnimationFrame(update);
      }
    };

    setTimeout(update, 300);
  });

  const cards = document.querySelectorAll(".animate-fade-in");
  cards.forEach((card, i) => {
    card.style.opacity = 0;
    card.style.transform = "translateY(20px)";
    setTimeout(() => {
      card.style.transition = "all 0.6s ease-out";
      card.style.opacity = 1;
      card.style.transform = "translateY(0)";
    }, 200 + i * 100);
  });
});


document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".counter");

  counters.forEach(counter => {
    const target = +counter.dataset.count;
    let count = 0;

    const update = () => {
      count += Math.max(1, Math.floor(target / 30));
      if (count >= target) {
        counter.textContent = target;
      } else {
        counter.textContent = count;
        requestAnimationFrame(update);
      }
    };

    setTimeout(update, 300);
  });

  const cards = document.querySelectorAll(".animate-fade-in");
  cards.forEach((card, i) => {
    card.style.opacity = 0;
    card.style.transform = "translateY(20px)";
    setTimeout(() => {
      card.style.transition = "all 0.6s ease-out";
      card.style.opacity = 1;
      card.style.transform = "translateY(0)";
    }, 200 + i * 100);
  });
});


document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".counter");

  counters.forEach(counter => {
    const target = +counter.dataset.count;
    let count = 0;

    const update = () => {
      count += Math.max(1, Math.floor(target / 30));
      if (count >= target) {
        counter.textContent = target;
      } else {
        counter.textContent = count;
        requestAnimationFrame(update);
      }
    };

    setTimeout(update, 300);
  });

  const cards = document.querySelectorAll(".animate-fade-in");
  cards.forEach((card, i) => {
    card.style.opacity = 0;
    card.style.transform = "translateY(20px)";
    setTimeout(() => {
      card.style.transition = "all 0.6s ease-out";
      card.style.opacity = 1;
      card.style.transform = "translateY(0)";
    }, 200 + i * 100);
  });
});