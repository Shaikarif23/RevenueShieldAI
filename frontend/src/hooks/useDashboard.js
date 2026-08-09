import { useCallback, useEffect, useState } from "react";
import { getOverview } from "../services/dashboardService";
import { getApiError } from "../services/api";

export function useDashboard(filters) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await getOverview(filters);
      setData(result);
    } catch (err) {
      setError(getApiError(err, "Unable to load dashboard."));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}