import { useEffect, useMemo, useState } from "react";

import { useDashboard } from "../hooks/useDashboard";
import { getRestaurants } from "../services/dashboardService";

import { getApiError } from "../services/api";

import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";

import SummaryCard from "../components/dashboard/SummaryCard";
import RiskCard from "../components/dashboard/RiskCard";
import DashboardFilters from "../components/dashboard/DashboardFilters";
import RevenueChart from "../components/dashboard/RevenueChart";
import LeakageChart from "../components/dashboard/LeakageChart";
import RestaurantLeakageTable from "../components/dashboard/RestaurantLeakageTable";
import TopLeakedOrders from "../components/dashboard/TopLeakedOrders";
import RecentAnomalies from "../components/dashboard/RecentAnomalies";
import AlertsPanel from "../components/dashboard/AlertsPanel";

import { formatCurrency } from "../utils/formatCurrency";
import { formatPercentage } from "../utils/formatPercentage";


const initialFilters = {
  restaurant_id: "",
  from_date: "",
  to_date: "",
  risk_level: "",
};


export default function Dashboard() {
  // =========================================================
  // FILTER STATE
  // =========================================================

  const [filters, setFilters] = useState(initialFilters);

  const [appliedFilters, setAppliedFilters] =
    useState(initialFilters);


  // =========================================================
  // RESTAURANTS
  // =========================================================

  const [restaurants, setRestaurants] = useState([]);

  const [restaurantError, setRestaurantError] =
    useState("");


  // =========================================================
  // MAIN DASHBOARD DATA
  // =========================================================

  const {
    data,
    loading,
    error,
    reload,
  } = useDashboard(appliedFilters);


  // =========================================================
  // LOAD RESTAURANTS
  // =========================================================

  useEffect(() => {
    let mounted = true;

    async function loadRestaurants() {
      try {
        setRestaurantError("");

        const result = await getRestaurants();

        if (!mounted) {
          return;
        }

        setRestaurants(result.data || []);
      } catch (err) {
        if (!mounted) {
          return;
        }

        setRestaurantError(
          getApiError(
            err,
            "Unable to load restaurants."
          )
        );
      }
    }

    loadRestaurants();

    return () => {
      mounted = false;
    };
  }, []);


  // =========================================================
  // DASHBOARD DATA
  // =========================================================

  const summary = data?.summary || {};

  const risk = data?.risk_summary || {};

  const restaurantLeakage =
    data?.restaurant_leakage || [];


  // =========================================================
  // DATE VALIDATION
  // =========================================================

  const canApply = useMemo(
    () =>
      !(
        filters.from_date &&
        filters.to_date &&
        filters.from_date > filters.to_date
      ),
    [filters]
  );


  // =========================================================
  // APPLY FILTERS
  // =========================================================

  function applyFilters() {
    if (!canApply) {
      return;
    }

    setAppliedFilters({
      ...filters,
    });
  }


  // =========================================================
  // CLEAR FILTERS
  // =========================================================

  function clearFilters() {
    setFilters(initialFilters);

    setAppliedFilters(initialFilters);
  }


  // =========================================================
  // INITIAL LOADING
  // =========================================================

  if (loading && !data) {
    return (
      <Loading
        text="Loading RevenueShield dashboard..."
      />
    );
  }


  // =========================================================
  // MAIN DASHBOARD ERROR
  // =========================================================

  if (error && !data) {
    return (
      <ErrorMessage
        message={error}
        onRetry={reload}
      />
    );
  }


  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="dashboard-page">

      {/* =====================================================
          FILTERS
      ====================================================== */}

      <DashboardFilters
        filters={filters}
        setFilters={setFilters}
        restaurants={restaurants}
        onApply={applyFilters}
        onClear={clearFilters}
      />


      {/* =====================================================
          FILTER VALIDATION ERROR
      ====================================================== */}

      {!canApply && (
        <div className="filter-error">
          From date cannot be later than To date.
        </div>
      )}


      {/* =====================================================
          RESTAURANT ERROR
      ====================================================== */}

      {restaurantError && (
        <div className="filter-error">
          {restaurantError}
        </div>
      )}


      {/* =====================================================
          DASHBOARD ERROR
      ====================================================== */}

      {error && (
        <ErrorMessage
          message={error}
          onRetry={reload}
        />
      )}


      {/* =====================================================
          SUMMARY CARDS
      ====================================================== */}

      <div className="summary-grid">

        <SummaryCard
          label="Expected Revenue"
          value={formatCurrency(
            summary.total_expected_revenue
          )}
          hint={`${summary.total_orders || 0} total orders`}
        />

        <SummaryCard
          label="Collected Revenue"
          value={formatCurrency(
            summary.total_collected_revenue
          )}
          hint="Successful payments"
        />

        <SummaryCard
          label="Actual Leakage"
          value={formatCurrency(
            summary.total_leakage
          )}
          hint="Delivered orders only"
          tone="danger"
        />

        <SummaryCard
          label="Leakage Rate"
          value={formatPercentage(
            summary.leakage_percentage
          )}
          hint="Delivered revenue basis"
          tone="warning"
        />

      </div>


      {/* =====================================================
          RISK SUMMARY
      ====================================================== */}

      <div className="risk-grid">

        <RiskCard
          level="HIGH"
          count={risk.high_risk || 0}
        />

        <RiskCard
          level="MEDIUM"
          count={risk.medium_risk || 0}
        />

        <RiskCard
          level="LOW"
          count={risk.low_risk || 0}
        />

        <div className="risk-summary-box">

          <span>
            Revenue leakage cases
          </span>

          <strong>
            {risk.revenue_leakage_anomalies || 0}
          </strong>

          <small>
            Data quality:{" "}
            {risk.data_quality_anomalies || 0}
          </small>

        </div>

      </div>


      {/* =====================================================
          CHARTS
      ====================================================== */}

      <div className="chart-grid">

        <RevenueChart
          restaurants={restaurantLeakage}
        />

        <LeakageChart
          summary={summary}
        />

      </div>


      {/* =====================================================
          RESTAURANT LEAKAGE + TOP ORDERS
      ====================================================== */}

      <div className="two-column">

        <RestaurantLeakageTable
          restaurants={restaurantLeakage}
        />

        <TopLeakedOrders
          orders={
            data?.top_leaked_orders || []
          }
        />

      </div>


      {/* =====================================================
          RECENT ANOMALIES + ALERTS
      ====================================================== */}

      <div className="two-column">

        <RecentAnomalies
          anomalies={
            data?.recent_anomalies || []
          }
        />


        <AlertsPanel
          alerts={data?.alerts || []}
        />

      </div>

    </div>
  );
}