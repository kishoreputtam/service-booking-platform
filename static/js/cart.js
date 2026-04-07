var SLOT_OPTIONS = {
  morning: [
    "08:00 AM - 09:00 AM",
    "09:00 AM - 10:00 AM",
    "10:00 AM - 11:00 AM"
  ],
  afternoon: [
    "12:00 PM - 01:00 PM",
    "01:00 PM - 02:00 PM",
    "02:00 PM - 03:00 PM"
  ],
  evening: [
    "04:00 PM - 05:00 PM",
    "05:00 PM - 06:00 PM",
    "06:00 PM - 07:00 PM"
  ]
};

function buildUpcomingDays() {
  var weekFormatter = new Intl.DateTimeFormat("en-US", { weekday: "short" });
  var dateFormatter = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" });
  var days = [];
  var i;

  for (i = 0; i < 4; i++) {
    var date = new Date();
    var label = "";

    date.setDate(date.getDate() + i);

    if (i === 0) {
      label = "Today";
    } else if (i === 1) {
      label = "Tomorrow";
    } else {
      label = weekFormatter.format(date);
    }

    days.push({
      value: date.toISOString().slice(0, 10),
      label: label,
      sublabel: dateFormatter.format(date)
    });
  }

  return days;
}

var UPCOMING_DAYS = buildUpcomingDays();
var selectedPeriod = "morning";
var selectedSlot = SLOT_OPTIONS.morning[0];
var selectedDay = UPCOMING_DAYS.length > 0 ? UPCOMING_DAYS[0].value : "";

function getCart() {
  var cartText = localStorage.getItem("cart");
  if (!cartText) {
    return [];
  }
  return JSON.parse(cartText);
}

function clearCart() {
  localStorage.removeItem("cart");
  location.reload();
}

function isUserLoggedIn() {
  var body = document.body;
  if (!body) {
    return false;
  }
  return body.getAttribute("data-logged-in") === "1";
}

function hasLoginError() {
  var body = document.body;
  if (!body) {
    return false;
  }
  return body.getAttribute("data-login-error") === "1";
}

function hasRegisterError() {
  var body = document.body;
  if (!body) {
    return false;
  }
  return body.getAttribute("data-register-error") === "1";
}

function getPageMessage() {
  var body = document.body;
  if (!body) {
    return "";
  }
  return body.getAttribute("data-page-message") || "";
}

function isPageMessageError() {
  var body = document.body;
  if (!body) {
    return false;
  }
  return body.getAttribute("data-page-message-type") === "error";
}

function openCartAuthModal() {
  var modal = document.getElementById("modal");
  var login = document.getElementById("login");
  var register = document.getElementById("register");

  if (!modal) {
    return;
  }

  if (login && register) {
    login.style.display = "block";
    register.style.display = "none";
  }

  modal.style.display = "flex";

  setTimeout(function () {
    modal.classList.add("show");
  }, 10);
}

function closeCartAuthModal() {
  var modal = document.getElementById("modal");
  if (!modal) {
    return;
  }

  modal.classList.remove("show");

  setTimeout(function () {
    modal.style.display = "none";
  }, 300);
}

function toggleCartAuthForm() {
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

function setCheckoutMessage(message, isError) {
  var messageEl = document.getElementById("checkoutMessage");
  if (!messageEl) {
    return;
  }

  messageEl.textContent = message || "";

  if (isError) {
    messageEl.style.color = "#c62828";
  } else {
    messageEl.style.color = "#2e5b27";
  }
}

function renderCart() {
  var cart = getCart();
  var container = document.getElementById("cart-items");
  var totalEl = document.getElementById("total");
  var checkoutBtn = document.getElementById("checkoutBtn");
  var total = 0;
  var i;

  if (!container || !totalEl) {
    return;
  }

  if (cart.length === 0) {
    container.innerHTML = '<p class="empty-state">Your cart is empty.</p>';
    totalEl.innerText = "₹0";
    if (checkoutBtn) {
      checkoutBtn.disabled = true;
    }
    return;
  }

  container.innerHTML = "";

  for (i = 0; i < cart.length; i++) {
    var item = cart[i];
    var itemTotal = item.price * item.qty;
    var card = document.createElement("div");

    total = total + itemTotal;
    card.className = "group";
    card.innerHTML =
      "<h3>" + item.name + "</h3>" +
      "<small>" + (item.pageCategory || item.category) + " • Qty " + item.qty + "</small>" +
      '<div class="service">₹' + item.price + " each</div>" +
      '<div class="service">Item total: ₹' + itemTotal + "</div>";
    container.appendChild(card);
  }

  totalEl.innerText = "₹" + total;
  if (checkoutBtn) {
    checkoutBtn.disabled = false;
  }
}

function renderSlotOptions(period) {
  var slotContainer = document.getElementById("slot-options");
  var slots = SLOT_OPTIONS[period] || [];
  var html = "";
  var i;

  if (!slotContainer) {
    return;
  }

  if (slots.indexOf(selectedSlot) === -1) {
    selectedSlot = slots.length > 0 ? slots[0] : "";
  }

  for (i = 0; i < slots.length; i++) {
    html += '<button type="button" class="slot-option';
    if (slots[i] === selectedSlot) {
      html += ' active';
    }
    html += '" data-slot="' + slots[i] + '">' + slots[i] + "</button>";
  }

  slotContainer.innerHTML = html;

  var buttons = slotContainer.querySelectorAll(".slot-option");
  for (i = 0; i < buttons.length; i++) {
    buttons[i].onclick = function () {
      selectedSlot = this.getAttribute("data-slot");
      renderSlotOptions(selectedPeriod);
    };
  }
}

function renderDayOptions() {
  var dayContainer = document.getElementById("slot-days");
  var html = "";
  var i;

  if (!dayContainer) {
    return;
  }

  for (i = 0; i < UPCOMING_DAYS.length; i++) {
    html += '<button type="button" class="slot-day';
    if (UPCOMING_DAYS[i].value === selectedDay) {
      html += ' active';
    }
    html += '" data-day="' + UPCOMING_DAYS[i].value + '">';
    html += "<strong>" + UPCOMING_DAYS[i].label + "</strong>";
    html += "<span>" + UPCOMING_DAYS[i].sublabel + "</span>";
    html += "</button>";
  }

  dayContainer.innerHTML = html;

  var buttons = dayContainer.querySelectorAll(".slot-day");
  for (i = 0; i < buttons.length; i++) {
    buttons[i].onclick = function () {
      selectedDay = this.getAttribute("data-day");
      renderDayOptions();
    };
  }
}

function initializeSlotSelector() {
  var buttons = document.querySelectorAll(".slot-period");
  var i;

  renderDayOptions();

  for (i = 0; i < buttons.length; i++) {
    buttons[i].onclick = function () {
      var allButtons = document.querySelectorAll(".slot-period");
      var j;

      for (j = 0; j < allButtons.length; j++) {
        allButtons[j].classList.remove("active");
      }

      this.classList.add("active");
      selectedPeriod = this.getAttribute("data-period");
      selectedSlot = SLOT_OPTIONS[selectedPeriod][0];
      renderSlotOptions(selectedPeriod);
    };
  }

  renderSlotOptions(selectedPeriod);
}

function initializePaymentSelector() {
  var inputs = document.querySelectorAll(".payment-choice input");
  var i;

  for (i = 0; i < inputs.length; i++) {
    inputs[i].onchange = function () {
      var choices = document.querySelectorAll(".payment-choice");
      var j;

      for (j = 0; j < choices.length; j++) {
        choices[j].classList.remove("active");
      }

      if (this.parentElement && this.parentElement.classList.contains("payment-choice")) {
        this.parentElement.classList.add("active");
      } else if (this.closest(".payment-choice")) {
        this.closest(".payment-choice").classList.add("active");
      }
    };
  }
}

function getSelectedPaymentMethod() {
  var selected = document.querySelector('input[name="payment_method"]:checked');
  if (!selected) {
    return "";
  }
  return selected.value;
}

function setLocationMessage(message, isError) {
  var locationMessage = document.getElementById("cartLocationMessage");
  if (!locationMessage) {
    return;
  }

  locationMessage.textContent = message || "";

  if (isError) {
    locationMessage.style.color = "#c62828";
  } else {
    locationMessage.style.color = "#4f4f4f";
  }
}

function updateLocationFields(lat, lng) {
  var latInput = document.getElementById("cartLocationLat");
  var lngInput = document.getElementById("cartLocationLng");

  if (latInput) {
    latInput.value = lat;
  }
  if (lngInput) {
    lngInput.value = lng;
  }
}

function updatePlaceId(placeId) {
  var placeIdInput = document.getElementById("cartLocationPlaceId");
  if (placeIdInput) {
    placeIdInput.value = placeId || "";
  }
}

function fillLocationFromCoords(lat, lng) {
  var locationInput = document.getElementById("cartLocationInput");

  updateLocationFields(lat, lng);
  updatePlaceId("");

  if (!locationInput) {
    return;
  }

  if (window.google && google.maps && google.maps.Geocoder) {
    var geocoder = new google.maps.Geocoder();

    geocoder.geocode({ location: { lat: lat, lng: lng } }, function (results, status) {
      if (status === "OK" && results && results.length > 0) {
        locationInput.value = results[0].formatted_address;
        updatePlaceId(results[0].place_id || "");
      } else {
        locationInput.value = "Location detected";
      }

      setLocationMessage("Location ready for checkout.", false);
    });
  } else {
    locationInput.value = "Location detected";
    setLocationMessage("Location ready for checkout.", false);
  }
}

function getUserLocation() {
  if (!navigator.geolocation) {
    setLocationMessage("Geolocation not supported.", true);
    return;
  }

  setLocationMessage("Detecting your location...", false);

  navigator.geolocation.getCurrentPosition(
    function (position) {
      fillLocationFromCoords(position.coords.latitude, position.coords.longitude);
    },
    function () {
      setLocationMessage("Unable to detect location.", true);
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  );
}

function initCartLocationServices() {
  var locationInput = document.getElementById("cartLocationInput");
  var detectButton = document.getElementById("cartDetectLocationBtn");

  if (detectButton) {
    detectButton.onclick = getUserLocation;
  }

  if (!locationInput || !(window.google && google.maps && google.maps.places)) {
    return;
  }

  var autocomplete = new google.maps.places.Autocomplete(locationInput, {
    fields: ["formatted_address", "geometry", "name", "place_id"],
    types: ["geocode"]
  });

  autocomplete.addListener("place_changed", function () {
    var place = autocomplete.getPlace();

    if (!place) {
      return;
    }

    locationInput.value = place.formatted_address || place.name || locationInput.value;
    updatePlaceId(place.place_id || "");

    if (place.geometry && place.geometry.location) {
      updateLocationFields(place.geometry.location.lat(), place.geometry.location.lng());
      setLocationMessage("Location ready for checkout.", false);
    }
  });
}

function checkout() {
  var cart = getCart();
  var addressInputBox = document.getElementById("cartLocationInput");
  var address = addressInputBox ? addressInputBox.value.trim() : "";
  var paymentMethod = getSelectedPaymentMethod();
  var selectedDayInfo = null;
  var checkoutForm = document.getElementById("checkoutForm");
  var cartItemsInput = document.getElementById("checkoutCartItems");
  var addressInput = document.getElementById("checkoutAddress");
  var latitudeInput = document.getElementById("checkoutLatitude");
  var longitudeInput = document.getElementById("checkoutLongitude");
  var placeIdInput = document.getElementById("checkoutPlaceId");
  var slotPeriodInput = document.getElementById("checkoutSlotPeriod");
  var slotTimeInput = document.getElementById("checkoutSlotTime");
  var paymentInput = document.getElementById("checkoutPaymentMethod");
  var cartLatInput = document.getElementById("cartLocationLat");
  var cartLngInput = document.getElementById("cartLocationLng");
  var cartPlaceIdInput = document.getElementById("cartLocationPlaceId");
  var cartText = "";
  var i;

  for (i = 0; i < UPCOMING_DAYS.length; i++) {
    if (UPCOMING_DAYS[i].value === selectedDay) {
      selectedDayInfo = UPCOMING_DAYS[i];
      break;
    }
  }

  if (cart.length === 0) {
    setCheckoutMessage("Your cart is empty.", true);
    return;
  }

  if (!isUserLoggedIn()) {
    setCheckoutMessage("Please login to continue.", true);
    openCartAuthModal();
    return;
  }

  if (!selectedDay || !selectedPeriod || !selectedSlot) {
    setCheckoutMessage("Please choose a time slot.", true);
    return;
  }

  if (!address) {
    setCheckoutMessage("Please choose your service address.", true);
    return;
  }

  if (!paymentMethod) {
    setCheckoutMessage("Please choose a payment option.", true);
    return;
  }

  if (paymentMethod === "online_payment") {
    setCheckoutMessage("Razorpay checkout will be added next. Use Pay After Service for now.", true);
    return;
  }

  if (!checkoutForm || !cartItemsInput || !addressInput || !latitudeInput || !longitudeInput || !placeIdInput || !slotPeriodInput || !slotTimeInput || !paymentInput) {
    setCheckoutMessage("Unable to place order.", true);
    return;
  }

  for (i = 0; i < cart.length; i++) {
    if (i > 0) {
      cartText += "||";
    }
    cartText += cart[i].name + "##" + cart[i].price + "##" + cart[i].qty + "##" + (cart[i].pageCategory || cart[i].category || "");
  }

  cartItemsInput.value = cartText;
  addressInput.value = address;
  latitudeInput.value = cartLatInput ? cartLatInput.value : "";
  longitudeInput.value = cartLngInput ? cartLngInput.value : "";
  placeIdInput.value = cartPlaceIdInput ? cartPlaceIdInput.value : "";
  slotPeriodInput.value = selectedPeriod;

  if (selectedDayInfo) {
    slotTimeInput.value = selectedDayInfo.label + ", " + selectedDayInfo.sublabel + " - " + selectedSlot;
  } else {
    slotTimeInput.value = selectedDay + " - " + selectedSlot;
  }

  paymentInput.value = paymentMethod;
  checkoutForm.submit();
}

document.addEventListener("DOMContentLoaded", function () {
  var checkoutBtn = document.getElementById("checkoutBtn");
  var detectButton = document.getElementById("cartDetectLocationBtn");

  renderCart();
  initializeSlotSelector();
  initializePaymentSelector();

  if (checkoutBtn) {
    checkoutBtn.onclick = checkout;
  }

  if (detectButton) {
    detectButton.onclick = getUserLocation;
  }

  if (hasLoginError()) {
    openCartAuthModal();
  }

  if (hasRegisterError()) {
    toggleCartAuthForm();
    openCartAuthModal();
  }

  if (getPageMessage()) {
    setCheckoutMessage(getPageMessage(), isPageMessageError());
  }
});

window.initCartLocationServices = initCartLocationServices;
