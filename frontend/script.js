document.addEventListener("DOMContentLoaded", async () => {
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  const signupBtn = document.getElementById("signup-btn");
  const loginMsg = document.getElementById("login-msg");
  const signupMsg = document.getElementById("signup-msg");

  const inDashboard = window.location.pathname.includes("dashboard.html");

  // ========== DASHBOARD PAGE LOGIC ==========
  if (inDashboard) {
    const token = localStorage.getItem("access_token");
    const msg = document.getElementById("dashboard-msg");

    if (!token) {
      window.location.href = "index.html";
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:5000/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
        return;
      }

      const data = await res.json();
      document.getElementById("fullname").value = data.full_name || "";
      document.getElementById("address").value = data.address || "";
      document.getElementById("phone").value = data.phone_number || "";
      document.querySelector(".dashboard-title").textContent = `Welcome ${data.full_name || "User"}`;

      // Save Details
      document.getElementById("save-details-btn").addEventListener("click", async () => {
        const updatedProfile = {
          full_name: document.getElementById("fullname").value.trim(),
          address: document.getElementById("address").value.trim(),
          phone_number: document.getElementById("phone").value.trim(),
        };

        try {
          const putRes = await fetch("http://127.0.0.1:5000/profile", {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(updatedProfile),
          });

          const result = await putRes.json();

          if (putRes.ok) {
            msg.style.color = "green";
            msg.textContent = result.message || "Profile updated successfully.";
          } else {
            msg.style.color = "red";
            switch (putRes.status) {
              case 402:
                msg.textContent = "Full name must be 20 characters or fewer.";
                break;
              case 403:
                msg.textContent = "Address must be 20 characters or fewer.";
                break;
              case 404:
                msg.textContent = "Invalid Israeli phone number.";
                break;
              case 405:
                msg.textContent = "User not found.";
                break;
              default:
                msg.textContent = result.error || "Update failed.";
            }
          }
        } catch (err) {
          msg.style.color = "red";
          msg.textContent = "Network error.";
        }
      });


      // Logout
      document.getElementById("logout-btn")?.addEventListener("click", () => {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
      });

    } catch (err) {
      console.error("Error fetching profile", err);
      localStorage.removeItem("access_token");
      window.location.href = "index.html";
    }

    return;
  }

  // ========== AUTH PAGE LOGIC ==========
  const verifyFields = document.getElementById("verify-fields");
  const signupFields = document.getElementById("signup-fields");
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

  document.querySelectorAll(".password-field input").forEach(input => {
    const toggle = input.parentElement.querySelector(".toggle-password");
    toggle.style.visibility = "hidden";
    input.addEventListener("input", () => {
      toggle.style.visibility = input.value.length > 0 ? "visible" : "hidden";
    });
  });

  signupBtn?.addEventListener("click", async () => {
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

  loginForm?.addEventListener("submit", async (e) => {
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

      if (res.status === 429) {
        loginMsg.style.color = "red";
        loginMsg.textContent = "You have exceeded the number of login attempts. Please try again in a minute.";
        return;
      }

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

  // Toggle password visibility
  document.querySelectorAll(".password-field input").forEach(input => {
    const toggle = input.parentElement.querySelector(".toggle-password");
    const img = toggle.querySelector("img");

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
