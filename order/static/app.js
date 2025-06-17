document.addEventListener("DOMContentLoaded", () => {
  let cart = [];
  const uploadSection = document.querySelector(".uploaded-files-cards");
  const form = document.getElementById("uploadForm");
  const fileInput = form.querySelector('input[type="file"]');
  const addToCartBtn = document.getElementById("addToCartBtn");
  const submitOrderBtn = document.getElementById("submitOrderBtn");
  const configPanel = document.querySelector("#config-panel");
  const groupToggle = document.querySelector("#group-toggle-button");

  // how uploaded files immediately after selection
  fileInput.addEventListener("change", (e) => {
    document.querySelector(".uploaded-file-container").style.display = "block";

    uploadSection.innerHTML = ""; // Clear previous entries

    const files = e.target.files;

    for (let file of files) {
      let fileCard = document.createElement("div");
      fileCard.classList.add("file-card");

      let fileName = document.createElement("p");
      fileName.textContent = file.name;
      const sizeInBytes = file.size;
      const sizeInKB = (sizeInBytes / 1024).toFixed(2);
      const sizeInMB = (sizeInBytes / (1024 * 1024)).toFixed(2);

      let fileSize = document.createElement("div");
      fileSize.classList.add("filesize")

      fileSize.innerHTML = `
            <p>${sizeInMB > 1 ? sizeInMB + " MB" : sizeInKB + " KB"}</p>
        `;

      let configButton = document.createElement("button");
      configButton.textContent = "Configure";
      configButton.classList.add("config-btn");
      configButton.type = "button";
      configButton.addEventListener("click", () => {
        configPanel.style.display = "block";
      });

      fileCard.appendChild(fileName);
      fileCard.appendChild(fileSize);
      fileCard.appendChild(configButton);
      uploadSection.appendChild(fileCard);
    }

    updateGrouping();
  });

  // Handle file grouping toggle
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
        groupedConfigButton.addEventListener("click", () => {
          configPanel.style.display = "block";
        });
      }
    } else {
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

  // ✅ "Add to Cart" Click Event (Handles File Upload + Configuration)
  addToCartBtn.addEventListener("click", async (e) => {
    e.preventDefault(); // Prevent form submission
    configPanel.style.display = "none";
    const formData = new FormData();
    const files = fileInput.files;

    if (files.length === 0) {
      alert("Please upload a file before adding to cart.");
      return;
    }

    for (let file of files) {
      formData.append("files", file);
    }

    // ✅ Include all necessary form fields for backend processing
    formData.append("layout", form.layout.value);
    formData.append("orientation", form.orientation.value);
    formData.append("color_mode", form.color_mode.value);
    formData.append("paper_size", form.paper_size.value);
    formData.append("insert_blank_pages", form.insert_blank_pages.checked);
    formData.append("duplex", form.duplex.checked);
    formData.append("pages", form.pages.value);
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
        document.querySelector("#totalCost").innerHTML = `RM ${data.cost}`
        renderCart(); // ✅ Update cart display
      } else {
        alert("Upload error.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to upload. Try again.");
    }
  });

  // ✅ "Submit Order" Form Submission (Finalizes Order)
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (cart.length === 0) {
      alert("Your cart is empty. Please add files before submitting.");
      return;
    }

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

    try {
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
    } catch (err) {
      console.error(err);
      alert("Failed to submit order.");
    }
  });

  function renderCart() {
    const cartDiv = document.getElementById("cart");
    cartDiv.innerHTML = "";

    cart.forEach((item) => {
      cartDiv.innerHTML += `
        <div class="cart-item">
          <p class="renamed-filename"><strong>${item.filename}</strong></p>
          <div class="cart-item-summary">
            <p>Pages: ${item.page_count}</p>
            <p>Cost: RM${item.cost}</p>
            <p>Layout: ${item.config.layout}</p>
            <p>Orientation: ${item.config.orientation}</p>
            <p>Color Mode: ${item.config.color_mode}</p>
            <p>Paper Size: ${item.config.paper_size}</p>
            <p>Duplex: ${item.config.duplex ? "Yes" : "No"}</p>
            <p>Quantity: ${item.config.qty}</p>
          </div>
          <p><a href="${
            item.preview_url
          } class="preview-url"" target="_blank">Download Preview</a></p>
        </div>
      `;
    });

    const total = cart.reduce((sum, item) => sum + parseFloat(item.cost), 0);
    cartDiv.innerHTML += `<p><strong>Total: RM${total.toFixed(2)}</strong></p>`;
  }
});
