function updateStockBadge(variantId, quantity, status) {
    const badge = document.getElementById(`stock-badge-${variantId}`);
    if (!badge) return;

    // Reset badge classes
    badge.classList.remove("bg-success", "bg-warning", "bg-danger", "text-dark");

    // Apply new color based on status
    if (status === "out") {
        badge.classList.add("bg-danger");
    } else if (status === "low") {
        badge.classList.add("bg-warning", "text-dark");
    } else {
        badge.classList.add("bg-success");
    }

    badge.textContent = quantity;
}
