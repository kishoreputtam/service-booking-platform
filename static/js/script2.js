function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function normalizePrice(text) {
  var digits = String(text || "").replace(/[^0-9]/g, "");
  if (digits) {
    return parseInt(digits, 10);
  }
  return 0;
}

function getCart() {
  var cartText = localStorage.getItem("cart");
  if (!cartText) {
    return [];
  }
  return JSON.parse(cartText);
}

function saveCart(cart) {
  localStorage.setItem("cart", JSON.stringify(cart));
}

function getCartCount() {
  var cart = getCart();
  var total = 0;
  var i;

  for (i = 0; i < cart.length; i++) {
    total = total + (cart[i].qty || 0);
  }

  return total;
}

function updateCartBadge(animate) {
  var cartCount = document.getElementById("serviceCartCount");
  var cartLink = document.getElementById("serviceCartLink");
  var count = getCartCount();

  if (!cartCount || !cartLink) {
    return;
  }

  if (count > 0) {
    cartCount.textContent = count + "+";
    cartCount.classList.add("visible");
    cartLink.classList.add("has-items");
  } else {
    cartCount.textContent = "1+";
    cartCount.classList.remove("visible");
    cartLink.classList.remove("has-items");
  }

  if (animate && count > 0) {
    cartCount.classList.remove("pop");
    void cartCount.offsetWidth;
    cartCount.classList.add("pop");
  }
}

function getCardData(button) {
  var card;
  var title;
  var priceText;
  var pageCategory;
  var category;
  var serviceKey;

  if (!button) {
    return null;
  }

  card = button.closest(".card");
  if (!card) {
    return null;
  }

  title = card.querySelector("h3");
  priceText = card.querySelector(".price");
  pageCategory = document.body.getAttribute("data-service-page");

  if (!pageCategory) {
    pageCategory = window.location.pathname.replace(/\//g, "");
  }
  if (!pageCategory) {
    pageCategory = "service";
  }

  category = button.getAttribute("data-cat") || card.getAttribute("data-cat") || pageCategory;
  serviceKey = pageCategory + "-" + slugify(title ? title.textContent.trim() : "service");

  button.setAttribute("data-cat", category);
  button.setAttribute("data-name", button.getAttribute("data-name") || (title ? title.textContent.trim() : "Service"));
  button.setAttribute("data-price", button.getAttribute("data-price") || String(normalizePrice(priceText ? priceText.textContent.trim() : "")));
  button.setAttribute("data-serviceKey", button.getAttribute("data-serviceKey") || serviceKey);
  button.setAttribute("data-pageCategory", button.getAttribute("data-pageCategory") || pageCategory);

  return {
    serviceKey: button.getAttribute("data-serviceKey"),
    pageCategory: button.getAttribute("data-pageCategory"),
    category: button.getAttribute("data-cat"),
    name: button.getAttribute("data-name"),
    price: parseInt(button.getAttribute("data-price"), 10) || 0
  };
}

function makeQtyControl(card) {
  var imgbox = card.querySelector(".imgbox");
  var qtyControl;

  if (!imgbox) {
    return null;
  }

  qtyControl = imgbox.querySelector(".qty-control");
  if (!qtyControl) {
    qtyControl = document.createElement("div");
    qtyControl.className = "qty-control";
    qtyControl.style.display = "none";
    qtyControl.innerHTML =
      '<button type="button" class="qty-decrease">-</button>' +
      "<span>1</span>" +
      '<button type="button" class="qty-increase">+</button>';
    imgbox.appendChild(qtyControl);
  }

  return qtyControl;
}

function filter(category, event) {
  var categories = document.querySelectorAll(".cat");
  var cards = document.querySelectorAll(".card");
  var i;

  for (i = 0; i < categories.length; i++) {
    categories[i].classList.remove("active");
  }

  if (event && event.currentTarget) {
    event.currentTarget.classList.add("active");
  }

  for (i = 0; i < cards.length; i++) {
    if (cards[i].getAttribute("data-cat") === category) {
      cards[i].style.display = "flex";
    } else {
      cards[i].style.display = "none";
    }
  }
}

function updateCardState(card, quantity) {
  var addButton;
  var qtyControl;
  var qtyValue;

  if (!card) {
    return;
  }

  addButton = card.querySelector(".add-btn");
  qtyControl = card.querySelector(".qty-control");
  qtyValue = qtyControl ? qtyControl.querySelector("span") : null;

  if (!addButton || !qtyControl || !qtyValue) {
    return;
  }

  if (quantity > 0) {
    addButton.style.display = "none";
    qtyControl.style.display = "flex";
    qtyValue.innerText = String(quantity);
  } else {
    addButton.style.display = "inline-block";
    qtyControl.style.display = "none";
    qtyValue.innerText = "1";
  }
}

function addToCart(item) {
  var cart = getCart();
  var found = false;
  var i;

  for (i = 0; i < cart.length; i++) {
    if (cart[i].serviceKey === item.serviceKey) {
      cart[i].qty = cart[i].qty + item.qty;
      found = true;
      break;
    }
  }

  if (!found) {
    cart.push(item);
  }

  saveCart(cart);
  updateCartBadge(true);
}

function updateCartItem(serviceKey, quantity) {
  var cart = getCart();
  var newCart = [];
  var i;

  for (i = 0; i < cart.length; i++) {
    if (cart[i].serviceKey === serviceKey) {
      cart[i].qty = quantity;
    }

    if (cart[i].qty > 0) {
      newCart.push(cart[i]);
    }
  }

  saveCart(newCart);
  updateCartBadge(false);
}

function findCartItem(serviceKey) {
  var cart = getCart();
  var i;

  for (i = 0; i < cart.length; i++) {
    if (cart[i].serviceKey === serviceKey) {
      return cart[i];
    }
  }

  return null;
}

function addItem(button) {
  var data = getCardData(button);
  var current;

  if (!data) {
    return;
  }

  addToCart({
    serviceKey: data.serviceKey,
    pageCategory: data.pageCategory,
    category: data.category,
    name: data.name,
    price: data.price,
    qty: 1
  });

  current = findCartItem(data.serviceKey);
  updateCardState(button.closest(".card"), current ? current.qty : 1);
}

function increase(button) {
  var card = button.closest(".card");
  var addButton = card ? card.querySelector(".add-btn") : null;
  var data = getCardData(addButton);
  var current;
  var nextQty;

  if (!card || !data) {
    return;
  }

  current = findCartItem(data.serviceKey);
  if (current) {
    nextQty = current.qty + 1;
  } else {
    nextQty = 1;
  }

  updateCartItem(data.serviceKey, nextQty);
  updateCardState(card, nextQty);
}

function decrease(button) {
  var card = button.closest(".card");
  var addButton = card ? card.querySelector(".add-btn") : null;
  var data = getCardData(addButton);
  var current;
  var nextQty;

  if (!card || !data) {
    return;
  }

  current = findCartItem(data.serviceKey);
  if (current) {
    nextQty = current.qty - 1;
  } else {
    nextQty = 0;
  }

  if (nextQty < 0) {
    nextQty = 0;
  }

  updateCartItem(data.serviceKey, nextQty);
  updateCardState(card, nextQty);
}

function initializeServiceCards() {
  var cards = document.querySelectorAll(".card");
  var i;

  for (i = 0; i < cards.length; i++) {
    var card = cards[i];
    var imgbox = card.querySelector(".imgbox");
    var addButton;
    var qtyControl;
    var decreaseButton;
    var increaseButton;
    var data;
    var existing;

    if (!imgbox) {
      continue;
    }

    addButton = imgbox.querySelector(".add-btn");
    if (!addButton) {
      addButton = imgbox.querySelector("button");
    }

    if (!addButton) {
      continue;
    }

    addButton.classList.add("add-btn");
    addButton.setAttribute("type", "button");
    addButton.removeAttribute("onclick");

    data = getCardData(addButton);
    qtyControl = makeQtyControl(card);
    decreaseButton = qtyControl ? qtyControl.querySelector(".qty-decrease") : null;
    increaseButton = qtyControl ? qtyControl.querySelector(".qty-increase") : null;

    addButton.onclick = function () {
      addItem(this);
    };

    if (decreaseButton) {
      decreaseButton.removeAttribute("onclick");
      decreaseButton.onclick = function () {
        decrease(this);
      };
    }

    if (increaseButton) {
      increaseButton.removeAttribute("onclick");
      increaseButton.onclick = function () {
        increase(this);
      };
    }

    existing = data ? findCartItem(data.serviceKey) : null;
    updateCardState(card, existing ? existing.qty : 0);
  }
}

function openFirstCategory() {
  var firstCategory = document.querySelector(".cat");
  var onclickText;
  var match;

  if (!firstCategory) {
    return;
  }

  onclickText = firstCategory.getAttribute("onclick") || "";
  match = onclickText.match(/'([^']+)'/);

  if (match && match[1]) {
    filter(match[1], { currentTarget: firstCategory });
  } else {
    filter(firstCategory.getAttribute("data-cat"), { currentTarget: firstCategory });
  }
}

window.addEventListener("DOMContentLoaded", function () {
  openFirstCategory();
  initializeServiceCards();
  updateCartBadge(false);
});
