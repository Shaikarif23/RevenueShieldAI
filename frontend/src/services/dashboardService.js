import api from "./api";

function buildParams(filters = {}, includeRisk = true) {
  const params = {};

  if (filters.restaurant_id !== undefined && filters.restaurant_id !== "") {
    params.restaurant_id = Number(filters.restaurant_id);
  }
  if (filters.from_date) params.from_date = filters.from_date;
  if (filters.to_date) params.to_date = filters.to_date;
  if (includeRisk && filters.risk_level) {
    params.risk_level = String(filters.risk_level).toUpperCase();
  }

  return params;
}

function unwrap(response) {
  return response.data;
}

export async function getOverview(filters = {}) {
  const response = await api.get("/dashboard/overview", {
    params: buildParams(filters, true),
  });
  return unwrap(response);
}

export async function getRevenue(filters = {}) {
  const response = await api.get("/dashboard/revenue", {
    params: buildParams(filters, true),
  });
  return unwrap(response);
}

export async function getRestaurantLeakage(filters = {}) {
  const response = await api.get("/dashboard/restaurant-leakage", {
    params: buildParams(filters, false),
  });
  return unwrap(response);
}

export async function getAnomalies(filters = {}) {
  const response = await api.get("/dashboard/anomalies", {
    params: buildParams(filters, true),
  });
  return unwrap(response);
}

export async function getAlerts(filters = {}) {
  const response = await api.get("/dashboard/alerts", {
    params: buildParams(filters, true),
  });
  return unwrap(response);
}

export async function getRestaurants(page = 1, size = 100, sort = "name_asc") {
  const response = await api.get("/restaurants/", {
    params: { page, size, sort },
  });
  return unwrap(response);
}

export async function getRestaurant(restaurantId) {
  const response = await api.get(`/restaurants/${restaurantId}`);
  return unwrap(response);
}
