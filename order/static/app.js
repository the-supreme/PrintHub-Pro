document.addEventListener("DOMContentLoaded", () => {
  let cart = [];
  const uploadSection = document.querySelector(".uploaded-files-cards");
  const form = document.getElementById("uploadForm");
  const fileInput = form.querySelector('input[type="file"]');
  const groupToggle = document.querySelector("#group-toggle-button");
  const configPanel = document.querySelector("#config-panel");
  fileInput.addEventListener("change", (e) => {
    document.querySelector(".uploaded-file-container").style.display = "block";

    uploadSection
      .querySelectorAll(".file-card")
      .forEach((card) => card.remove());

    const files = e.target.files;

    for (let file of files) {
      let fileCard = document.createElement("div");
      fileCard.classList.add("file-card");

      let fileName = document.createElement("p");
      fileName.textContent = file.name;

      let configButton = document.createElement("button");
      configButton.textContent = "Configure";
      configButton.classList.add("config-btn");
      configButton.type = "button";
      configButton.addEventListener("click", (e) => {
        configPanel.style.display = "block";
      });
      fileCard.appendChild(fileName);
      fileCard.appendChild(configButton);
      uploadSection.appendChild(fileCard);
    }

    updateGrouping();
  });

  groupToggle.addEventListener("change", () => {
    updateGrouping();
  });

  function updateGrouping() {
    const uploadedContainer = document.querySelector(
      ".uploaded-file-container"
    );

    if (groupToggle.checked) {
      let groupCardContainer = document.querySelector(".group-card-container");

      if (!groupCardContainer) {
        groupCardContainer = document.createElement("div");
        groupCardContainer.classList.add("group-card-container");
        uploadedContainer.appendChild(groupCardContainer);
      }

      groupCardContainer.appendChild(uploadSection);
      uploadSection
        .querySelectorAll(".config-btn")
        .forEach((btn) => btn.remove());

      // Add a single config button for the grouped files
      if (!groupCardContainer.querySelector(".group-config-btn")) {
        let groupedConfigButton = document.createElement("button");
        groupedConfigButton.textContent = "Configure Group";
        groupedConfigButton.classList.add("config-btn", "group-config-btn");
        groupCardContainer.appendChild(groupedConfigButton);
        groupedConfigButton.type = "button";
        groupedConfigButton.addEventListener("click", (e) => {
          configPanel.style.display = "block";
        });
      }
    } else {
      // Remove grouping and restore individual config buttons
      document.querySelector(".group-card-container")?.remove();

      uploadSection.querySelectorAll(".file-card").forEach((card) => {
        if (!card.querySelector(".config-btn")) {
          let configButton = document.createElement("button");
          configButton.textContent = "Configure";
          configButton.classList.add("config-btn");
          configButton.type = "button";
          card.appendChild(configButton);
        }
      });

      uploadedContainer.appendChild(uploadSection);
    }
  }

  form.addEventListener("submit", async (e) => {
    console.log("FORM SUBMITTED BY:", document.activeElement);
    e.preventDefault();

    const formData = new FormData();
    const files = fileInput.files;

    for (let file of files) {
      formData.append("files", file);
    }

    formData.append("layout", form.layout.value);
    formData.append("orientation", form.orientation.value);
    formData.append("color_mode", form.color_mode.value);
    formData.append("paper_size", form.paper_size.value);
    formData.append("insert_blank_pages", form.insert_blank_pages.checked);
    formData.append("duplex", form.duplex.checked);
    formData.append("pages", form.pages.value); // fixed
    formData.append("qty", form.qty.value);
    formData.append("phone_number", form.phone_number.value);

    try {
      const res = await fetch("/api/upload/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (res.ok) {
        cart.push({
          preview_url: data.preview_url,
          filename: data.renamed_filename,
          page_count: data.page_count,
          cost: data.cost,
          config: {
            layout: form.layout.value,
            orientation: form.orientation.value,
            color_mode: form.color_mode.value,
            paper_size: form.paper_size.value,
            duplex: form.duplex.checked,
            qty: form.qty.value,
          },
        });
        renderCart(); // ✅ Call render
      } else {
        alert("Upload error.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to upload. Try again.");
    }
  });

  function renderCart() {
    const cartDiv = document.getElementById("cart");
    cartDiv.innerHTML = "";

    cart.forEach((item) => {
      cartDiv.innerHTML += `
        <div class="cart-item">
          <p><strong>${item.filename}</strong></p>
          <p>Pages: ${item.page_count}, Cost: RM${item.cost}</p>
          <p><a href="${item.preview_url}" target="_blank">Download Preview</a></p>
          <hr>
        </div>
      `;
    });

    const total = cart.reduce((sum, item) => sum + parseFloat(item.cost), 0);
    cartDiv.innerHTML += `<p><strong>Total: RM${total.toFixed(2)}</strong></p>`;
  }

  document
    .getElementById("submitOrderBtn")
    .addEventListener("click", async () => {
      const name = document.getElementById("name").value;
      const email = document.getElementById("email").value;
      const phone = document.getElementById("phone").value;

      if (!name || !email || !phone) {
        alert("Please fill in your name, email, and phone.");
        return;
      }

      const total_cost = cart.reduce(
        (sum, item) => sum + parseFloat(item.cost),
        0
      );

      const res = await fetch("/api/submit-order/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, phone, total_cost }),
      });

      const data = await res.json();
      if (res.ok) {
        alert("Order Submitted!");
        cart = [];
        renderCart();
      } else {
        alert("Error submitting order.");
      }
    });
});
