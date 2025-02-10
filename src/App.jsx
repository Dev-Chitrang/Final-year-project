import { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [companyData, setCompanyData] = useState(null);
  const [creditRating, setCreditRating] = useState(null);
  const [vision, setVision] = useState("");
  const [mission, setMission] = useState("");
  const [visionMissionSentiment, setVisionMissionSentiment] = useState(null);
  const [investmentAnalysis, setInvestmentAnalysis] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:8000/companies")
      .then(res => {
        setCompanies(res.data);
      })
      .catch(err => console.error("Error fetching companies", err));
  }, []);

  const fetchCompanyData = async (ticker) => {
    try {
      const [summary, financials, trend, news, rating] = await Promise.all([
        axios.get(`http://localhost:8000/company-summary/${ticker}`),
        axios.get(`http://localhost:8000/financial-statements/${ticker}`),
        axios.get(`http://localhost:8000/stock-trend/${ticker}`),
        axios.get(`http://localhost:8000/sentiment-news/${ticker}`),
        axios.get(`http://localhost:8000/credit-rating/${ticker}`)
      ]);
      setCompanyData({
        summary: summary.data,
        financials: financials.data,
        trend: trend.data,
        news: news.data
      });
      setCreditRating(rating.data);
    } catch (error) {
      console.error("Error fetching company data", error);
    }
  };

  const handleSubmitVisionMission = async () => {
    try {
      const res = await axios.post("http://localhost:8000/vision-mission-sentiments", new URLSearchParams({ vision, mission }));
      setVisionMissionSentiment(res.data);
    } catch (error) {
      console.error("Error submitting vision/mission", error);
    }
  };

  const analyzeCompany = async () => {
    try {
      const res = await axios.post("http://localhost:8000/investment-analysis");
      setInvestmentAnalysis(res.data);
    } catch (error) {
      console.error("Error analyzing company", error);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Company Investment Analysis</h1>

      <select
        className="w-full p-2 border mb-4"
        onChange={(e) => {
          setSelectedCompany(e.target.value);
          fetchCompanyData(e.target.value);
        }}
        value={selectedCompany}
      >
        <option value="">Select a Company</option>
        {companies.map((comp) => (
          <option key={comp.Symbol} value={comp.Symbol}>
            {comp.Security}
          </option>
        ))}
      </select>

      {companyData && (
        <div className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold">Summary</h2>
            <p>{companyData.summary?.longBusinessSummary || "No summary available"}</p>
          </div>
          <div>
            <h2 className="text-xl font-semibold">Financial Statements</h2>
            <pre>{JSON.stringify(companyData.financials, null, 2)}</pre>
          </div>
          <div>
            <h2 className="text-xl font-semibold">Stock Trend</h2>
            <p>{companyData.trend?.current_trend || "No trend data available"}</p>
          </div>
          <div>
            <h2 className="text-xl font-semibold">News Sentiment</h2>
            <p>{companyData.news?.overall_sentiment || "No sentiment data available"}</p>
          </div>
          <div>
            <h2 className="text-xl font-semibold">Credit Rating</h2>
            <p>{creditRating?.ratings?.join(", ") || "No credit rating available"}</p>
          </div>
        </div>
      )}

      <div className="mt-6">
        <h2 className="text-xl font-semibold">Enter Vision & Mission</h2>
        <textarea
          className="w-full p-2 border mb-2"
          rows="3"
          placeholder="Enter Vision"
          value={vision}
          onChange={(e) => setVision(e.target.value)}
        />
        <textarea
          className="w-full p-2 border mb-2"
          rows="3"
          placeholder="Enter Mission"
          value={mission}
          onChange={(e) => setMission(e.target.value)}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2"
          onClick={handleSubmitVisionMission}
        >
          Submit
        </button>
      </div>

      {visionMissionSentiment && (
        <div className="mt-4">
          <h2 className="text-xl font-semibold">Vision & Mission Sentiment</h2>
          <p>{JSON.stringify(visionMissionSentiment)}</p>
        </div>
      )}

      <button
        className="mt-6 bg-green-500 text-white px-4 py-2"
        onClick={analyzeCompany}
      >
        Analyze Investment
      </button>

      {investmentAnalysis && (
        <div className="mt-4">
          <h2 className="text-xl font-semibold">Investment Analysis</h2>
          <p>{investmentAnalysis.investment_decision || "No decision available"}</p>
        </div>
      )}
    </div>
  );
}
