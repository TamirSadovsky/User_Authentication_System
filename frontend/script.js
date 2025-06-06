document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  const signupFields = document.getElementById("signup-fields");
  const verifyFields = document.getElementById("verify-fields");

  const loginMsg = document.getElementById("login-msg");
  const signupMsg = document.getElementById("signup-msg");

  const signupBtn = document.getElementById("signup-btn");
  const verifyBtn = document.getElementById("verify-btn");
  const resendBtn = document.getElementById("resend-btn");

  let inVerificationMode = false;

  document.getElementById("show-login").addEventListener("click", () => {
    if (inVerificationMode) return;
    loginForm.classList.add("active");
    signupForm.classList.remove("active");
    loginMsg.textContent = "";
    signupMsg.textContent = "";
  });

  document.getElementById("show-signup").addEventListener("click", () => {
    if (inVerificationMode) return;
    signupForm.classList.add("active");
    loginForm.classList.remove("active");
    loginMsg.textContent = "";
    signupMsg.textContent = "";
  });

  document.querySelectorAll(".toggle-password").forEach(toggle => {
    toggle.addEventListener("click", () => {
      const inputId = toggle.dataset.target;
      const input = document.getElementById(inputId);
      const img = toggle.querySelector("img");

      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      img.src = isHidden ? "eye-off.png" : "eye.png";
      img.alt = isHidden ? "Hide Password" : "Show Password";
    });
  });

  document.querySelectorAll(".password-field input").forEach(input => {
    const toggle = input.parentElement.querySelector(".toggle-password");

    // Hide initially
    toggle.style.visibility = "hidden";

    input.addEventListener("input", () => {
      toggle.style.visibility = input.value.length > 0 ? "visible" : "hidden";
    });
  });

  signupBtn.addEventListener("click", async () => {
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;
    const confirm = document.getElementById("signup-confirm").value;
    signupMsg.textContent = "";

    if (password !== confirm) {
      signupMsg.style.color = "red";
      signupMsg.textContent = "Passwords do not match.";
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (res.ok) {
        document.getElementById("signup-email").dataset.verifiedEmail = email;
        document.getElementById("verification-modal").classList.remove("hidden");
        inVerificationMode = true;
        alert("Signup successful. A verification code was sent to your email.");
      } else {
        signupMsg.style.color = "red";
        signupMsg.textContent = data.error || "Signup failed.";
      }
    } catch (err) {
      signupMsg.style.color = "red";
      signupMsg.textContent = "Network error.";
    }
  });

  verifyBtn.addEventListener("click", async () => {
    const email = document.getElementById("signup-email").dataset.verifiedEmail;
    const code = document.getElementById("verify-code").value.trim();

    try {
      const res = await fetch("http://127.0.0.1:5000/email_verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      });

      const data = await res.json();
      if (res.ok) {
        window.location.href = "dashboard.html";
      } else {
        signupMsg.style.color = "red";
        signupMsg.textContent = data.error || "Invalid verification code.";
      }
    } catch (err) {
      signupMsg.style.color = "red";
      signupMsg.textContent = "Network error.";
    }
  });

  resendBtn.addEventListener("click", async () => {
    const email = document.getElementById("signup-email").dataset.verifiedEmail;

    try {
      const res = await fetch("http://127.0.0.1:5000/resend_verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();
      signupMsg.style.color = res.ok ? "green" : "red";
      signupMsg.textContent = data.message || data.error;
    } catch (err) {
      signupMsg.style.color = "red";
      signupMsg.textContent = "Network error.";
    }
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const remember = document.getElementById("remember-me").checked;

    try {
      const res = await fetch("http://127.0.0.1:5000/logintoken", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, remember }),
      });

      const data = await res.json();
      if (res.ok && data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        window.location.href = "dashboard.html";
      } else {
        loginMsg.style.color = "red";
        loginMsg.textContent = data.error || "Login failed.";
      }
    } catch (err) {
      loginMsg.style.color = "red";
      loginMsg.textContent = "Network error.";
    }
  });


  // 👁️ Toggle password visibility
  document.querySelectorAll(".password-field input").forEach(input => {
    const toggle = input.parentElement.querySelector(".toggle-password");
    const img = toggle.querySelector("img");

    // Hide icon by default
    toggle.style.display = "none";

    input.addEventListener("input", () => {
      toggle.style.display = input.value ? "flex" : "none";
    });

    toggle.addEventListener("click", () => {
      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      img.src = isHidden ? "eye-off.png" : "eye.png";
      img.alt = isHidden ? "Hide Password" : "Show Password";
    });
  });

});
