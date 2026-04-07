function slideLeft() {
  var scrollContainer = document.getElementById("curationScroll");
  if (!scrollContainer) {
    return;
  }

  scrollContainer.scrollBy({
    left: -300,
    behavior: "smooth"
  });
}

function slideRight() {
  var scrollContainer = document.getElementById("curationScroll");
  if (!scrollContainer) {
    return;
  }

  scrollContainer.scrollBy({
    left: 300,
    behavior: "smooth"
  });
}

function updateSliderArrows() {
  var scrollContainer = document.getElementById("curationScroll");
  var leftArrow = document.querySelector(".arrow.left");
  var rightArrow = document.querySelector(".arrow.right");

  if (!scrollContainer) {
    return;
  }

  if (leftArrow) {
    if (scrollContainer.scrollLeft <= 0) {
      leftArrow.style.display = "none";
    } else {
      leftArrow.style.display = "flex";
    }
  }

  if (rightArrow) {
    if (scrollContainer.scrollLeft + scrollContainer.clientWidth >= scrollContainer.scrollWidth - 5) {
      rightArrow.style.display = "none";
    } else {
      rightArrow.style.display = "flex";
    }
  }
}

function startReviewScroll() {
  var scroll = document.querySelector(".reviews-scroll");
  if (!scroll) {
    return;
  }

  function autoScroll() {
    scroll.scrollLeft = scroll.scrollLeft + 1.5;

    if (scroll.scrollLeft >= scroll.scrollWidth / 2) {
      scroll.scrollLeft = 0;
    }

    requestAnimationFrame(autoScroll);
  }

  autoScroll();
}

function setupFaq() {
  var questions = document.querySelectorAll(".faq-question");
  var i;

  for (i = 0; i < questions.length; i++) {
    questions[i].addEventListener("click", function () {
      var items = document.querySelectorAll(".faq-item");
      var currentItem = this.parentElement;
      var j;

      for (j = 0; j < items.length; j++) {
        if (items[j] !== currentItem) {
          items[j].classList.remove("active");
        }
      }

      currentItem.classList.toggle("active");
    });
  }
}

function getNavbarCartCount() {
  var cartText = localStorage.getItem("cart");
  var cart = [];
  var total = 0;
  var i;

  if (cartText) {
    cart = JSON.parse(cartText);
  }

  for (i = 0; i < cart.length; i++) {
    total = total + (cart[i].qty || 0);
  }

  return total;
}

function clearCartAfterLogout() {
  var params = new URLSearchParams(window.location.search);
  var nextQuery = "";
  var nextUrl = "";

  if (params.get("logged_out") !== "1") {
    return;
  }

  localStorage.removeItem("cart");
  params.delete("logged_out");
  nextQuery = params.toString();
  nextUrl = window.location.pathname;

  if (nextQuery) {
    nextUrl = nextUrl + "?" + nextQuery;
  }

  nextUrl = nextUrl + window.location.hash;
  window.history.replaceState({}, document.title, nextUrl);
}

function updateNavbarCartBadge() {
  var badge = document.getElementById("navbarCartBadge");
  var link = document.getElementById("navbarCartLink");
  var count = getNavbarCartCount();

  if (!badge || !link) {
    return;
  }

  badge.textContent = count + "+";

  if (count > 0) {
    badge.classList.add("visible");
    link.classList.add("has-items");
  } else {
    badge.classList.remove("visible");
    link.classList.remove("has-items");
  }
}

function openModal() {
  var modal = document.getElementById("modal");
  if (!modal) {
    return;
  }

  modal.style.display = "flex";

  setTimeout(function () {
    modal.classList.add("show");
  }, 10);
}

function closeModal() {
  var modal = document.getElementById("modal");
  if (!modal) {
    return;
  }

  modal.classList.remove("show");

  setTimeout(function () {
    modal.style.display = "none";
  }, 300);
}

function toggleForm() {
  var login = document.getElementById("login");
  var register = document.getElementById("register");

  if (!login || !register) {
    return;
  }

  if (login.style.display === "none") {
    login.style.display = "block";
    register.style.display = "none";
  } else {
    login.style.display = "none";
    register.style.display = "block";
  }
}

function openLoginForOrders(event) {
  var login = document.getElementById("login");
  var register = document.getElementById("register");

  event.preventDefault();

  if (login && register) {
    login.style.display = "block";
    register.style.display = "none";
  }

  openModal();
}

function openProfessionalRegister(event) {
  var login = document.getElementById("login");
  var register = document.getElementById("register");
  var role = document.getElementById("role");

  if (event) {
    event.preventDefault();
  }

  if (login && register) {
    login.style.display = "none";
    register.style.display = "block";
  }

  if (role) {
    role.value = "provider";
  }

  openModal();
}

function openRegisterModal() {
  var login = document.getElementById("login");
  var register = document.getElementById("register");

  if (login && register) {
    login.style.display = "none";
    register.style.display = "block";
  }

  openModal();
}

function toggleAccountDropdown(event) {
  var dropdown = document.getElementById("accountDropdown");

  event.stopPropagation();

  if (!dropdown) {
    return;
  }

  dropdown.classList.toggle("show");
}

document.addEventListener("click", function (event) {
  var accountMenu = document.querySelector(".account-menu");
  var dropdown = document.getElementById("accountDropdown");

  if (!accountMenu || !dropdown) {
    return;
  }

  if (!accountMenu.contains(event.target)) {
    dropdown.classList.remove("show");
  }
});

window.addEventListener("storage", function (event) {
  if (event.key === "cart") {
    updateNavbarCartBadge();
  }
});

document.addEventListener("DOMContentLoaded", function () {
  var scrollContainer = document.getElementById("curationScroll");
  var body = document.body;
  var authMode = "";

  if (scrollContainer) {
    scrollContainer.addEventListener("scroll", updateSliderArrows);
    updateSliderArrows();
  }

  startReviewScroll();
  setupFaq();
  clearCartAfterLogout();
  updateNavbarCartBadge();

  if (body) {
    authMode = body.getAttribute("data-auth-mode") || "";

    if (body.getAttribute("data-login-error") === "1") {
      openModal();
    }

    if (body.getAttribute("data-register-error") === "1" || authMode === "register") {
      openRegisterModal();
    }
  }
});
