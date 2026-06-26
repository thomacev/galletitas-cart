
const API = "http://127.0.0.1:5000";

const IMAGENES = {
    1:  "img/donsatur.png",
    2:  "img/bagley.png",
    3:  "img/oreo.png",
    4:  "img/chocolinas.png",
    5:  "img/marmoladas.png",
    6:  "img/merengadas.png",
    7:  "img/pitusas.png",
    8:  "img/9deoro.png",
    9:  "img/diversion.png",
    10: "img/obleas.png",
    11: "img/pepitos.png",
    12: "img/canoncitos.png",
  };


  const $ = (sel) => document.querySelector(sel);

  function toast(msg) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2400);
  }

  function formatPrecio(n) {
    return "$" + Number(n).toLocaleString("es-AR", { minimumFractionDigits: 2 });
  }

  async function apiFetch(url, method = "GET") {
    const res = await fetch(API + url, { method });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

function visualProducto(p) {
  const src = IMAGENES[p.id];
  if (src) {
    return `<img
      class="producto-img"
      src="${src}"
      alt="${p.nombre}"
      id="img-producto-${p.id}"
      onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"
    /><div class="producto-placeholder" style="display:none">${p.nombre[0]}</div>`;
  }
  return `<div class="producto-placeholder">${p.nombre[0]}</div>`;
}

  let estadoCarrito = {}; // { [producto_id]: { nombre, cantidad, subtotal } }
//productos
  async function cargarProductos() {
    const cont = $("#lista-productos");
    try {
      const data = await apiFetch("/productos");
      const productos = data.productos;

      if (!productos.length) {
        cont.innerHTML = `<div class="vacio"><div class="emoji-vacio">🏪</div>No hay productos disponibles.</div>`;
        return;
      }

      cont.innerHTML = productos.map(p => `
        <div class="producto-card" id="producto-${p.id}" data-id="${p.id}" data-nombre="${p.nombre}">
          ${visualProducto(p)}
          <div class="nombre">${p.nombre}</div>
          <div class="precio">${formatPrecio(p.precio)}</div>
          <button
            class="btn-agregar"
            id="btn-agregar-${p.id}"
            data-id="${p.id}"
            aria-label="Agregar ${p.nombre} al carrito"
          >+ Agregar</button>
        </div>
      `).join("");

      cont.querySelectorAll(".btn-agregar").forEach(btn => {
        btn.addEventListener("click", () => agregarProducto(btn.dataset.id, btn));
      });

    } catch (e) {
      cont.innerHTML = `<div class="error-msg">Error al cargar productos: ${e.message}</div>`;
    }
  }

//carrito
  async function cargarCarritoInicial() {
    const listaCont = $("#lista-carrito");
    const resumenEl = $("#resumen-total");

    try {
      const [dataCarrito, dataTotal] = await Promise.all([
        apiFetch("/carrito"),
        apiFetch("/carrito/total")
      ]);

      const items = dataCarrito.carrito;

      // Actualizamos estado local
      estadoCarrito = {};
      items.forEach(item => { estadoCarrito[item.id] = item; });

      if (!items.length) {
        listaCont.innerHTML = `
          <div class="vacio" id="carrito-vacio">
            <div class="emoji-vacio">🛒</div>
            Tu carrito está vacío.<br>¡Agregá algo del catálogo!
          </div>`;
        resumenEl.hidden = true;
        return;
      }

      listaCont.innerHTML = items.map(item => crearItemHTML(item)).join("");
      adjuntarEventosCarrito(listaCont);

      resumenEl.hidden = false;
      $("#total-items").textContent = dataTotal.cantidad_items;
      $("#total-precio").textContent = formatPrecio(dataTotal.total);

    } catch (e) {
      listaCont.innerHTML = `<div class="error-msg">Error al cargar el carrito: ${e.message}</div>`;
      resumenEl.hidden = true;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // PATCH DEL CARRITO (después de cada acción — sin re-render completo)
  // ─────────────────────────────────────────────────────────────────────────
  async function actualizarCarrito() {
    const listaCont = $("#lista-carrito");
    const resumenEl = $("#resumen-total");

    // Indicamos visualmente que el total se está actualizando
    $("#total-precio").classList.add("updating");
    $("#total-items").classList.add("updating");

    try {
      const [dataCarrito, dataTotal] = await Promise.all([
        apiFetch("/carrito"),
        apiFetch("/carrito/total")
      ]);

      const items = dataCarrito.carrito;
      const nuevoEstado = {};
      items.forEach(item => { nuevoEstado[item.id] = item; });

      // ── 1. Eliminar items que ya no están ──
      Object.keys(estadoCarrito).forEach(id => {
        if (!nuevoEstado[id]) {
          const el = $(`#carrito-item-${id}`);
          if (el) el.remove();
        }
      });

      // ── 2. Carrito vacío después de eliminar ──
      if (!items.length) {
        listaCont.innerHTML = `
          <div class="vacio" id="carrito-vacio">
            <div class="emoji-vacio">🛒</div>
            Tu carrito está vacío.<br>¡Agregá algo del catálogo!
          </div>`;
        resumenEl.hidden = true;
        estadoCarrito = {};
        return;
      }

      // Remover vacio si existía
      const vacioPrev = $("#carrito-vacio");
      if (vacioPrev) vacioPrev.remove();

      items.forEach(item => {
        const existeEnDOM = $(`#carrito-item-${item.id}`);

        if (!existeEnDOM) {
          // ── 3. Item nuevo: insertar al final con animación ──
          const div = document.createElement("div");
          div.innerHTML = crearItemHTML(item, true);
          const nuevoItem = div.firstElementChild;
          listaCont.appendChild(nuevoItem);
          adjuntarEventosItem(nuevoItem);

        } else {
          // ── 4. Item existente: solo actualizar cantidad y subtotal ──
          const prev = estadoCarrito[item.id];
          if (!prev || prev.cantidad !== item.cantidad) {
            const qtyEl     = $(`#qty-${item.id}`);
            const subtotalEl = $(`#subtotal-${item.id}`);
            if (qtyEl)     qtyEl.textContent     = item.cantidad;
            if (subtotalEl) subtotalEl.textContent = formatPrecio(item.subtotal);
          }
        }
      });

      // ── 5. Actualizar resumen ──
      estadoCarrito = nuevoEstado;
      resumenEl.hidden = false;
      $("#total-items").textContent = dataTotal.cantidad_items;
      $("#total-precio").textContent = formatPrecio(dataTotal.total);

    } catch (e) {
      toast("Error al actualizar el carrito.");
    } finally {
      $("#total-precio").classList.remove("updating");
      $("#total-items").classList.remove("updating");
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // HELPERS DE DOM DEL CARRITO
  // ─────────────────────────────────────────────────────────────────────────
  function crearItemHTML(item, esNuevo = false) {
    return `
      <div class="carrito-item ${esNuevo ? 'item-nuevo' : ''}" id="carrito-item-${item.id}" data-id="${item.id}">
        <div class="item-nombre">${item.nombre}</div>
        <div class="qty-control">
          <button
            class="btn-qty btn-quitar"
            id="btn-quitar-${item.id}"
            data-id="${item.id}"
            aria-label="Quitar una unidad de ${item.nombre}"
          >−</button>
          <span id="qty-${item.id}" class="item-qty">${item.cantidad}</span>
          <button
            class="btn-qty btn-sumar"
            id="btn-sumar-${item.id}"
            data-id="${item.id}"
            aria-label="Agregar otra unidad de ${item.nombre}"
          >+</button>
        </div>
        <div class="item-subtotal" id="subtotal-${item.id}">${formatPrecio(item.subtotal)}</div>
      </div>`;
  }

  function adjuntarEventosItem(itemEl) {
    itemEl.querySelector(".btn-quitar")
      ?.addEventListener("click", (e) => quitarProducto(e.currentTarget.dataset.id));
    itemEl.querySelector(".btn-sumar")
      ?.addEventListener("click", (e) => agregarProducto(e.currentTarget.dataset.id));
  }

  function adjuntarEventosCarrito(cont) {
    cont.querySelectorAll(".carrito-item").forEach(adjuntarEventosItem);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // ACCIONES
  // ─────────────────────────────────────────────────────────────────────────
  async function agregarProducto(id, btnEl = null) {
    if (btnEl) { btnEl.disabled = true; btnEl.textContent = "…"; }
    try {
      const data = await apiFetch(`/carrito/${id}`, "POST");
      toast(data.mensaje);
      await actualizarCarrito();
    } catch (e) {
      toast("No se pudo agregar el producto.");
    } finally {
      if (btnEl) { btnEl.disabled = false; btnEl.textContent = "+ Agregar"; }
    }
  }

  async function quitarProducto(id) {
    try {
      const data = await apiFetch(`/carrito/${id}`, "DELETE");
      toast(data.mensaje);
      await actualizarCarrito();
    } catch (e) {
      toast("No se pudo quitar el producto.");
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // INIT
  // ─────────────────────────────────────────────────────────────────────────
  cargarProductos();
  cargarCarritoInicial();
