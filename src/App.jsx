import { useState, useEffect } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

export default function App() {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [companyData, setCompanyData] = useState(null);
  const [creditRating, setCreditRating] = useState(null);
  const [vision, setVision] = useState("");
  const [mission, setMission] = useState("");
  const [visionMissionSentiment, setVisionMissionSentiment] = useState(null);
  const [investmentAnalysis, setInvestmentAnalysis] = useState(null);
  const [forecastPlot, setForecastPlot] = useState(null);
  const [stockPlot, setStockPlot] = useState(null);
  const [trendComponents, setTrendComponents] = useState(null);
  const [errorMessage, setErrorMessage] = useState(""); // Added error handling

  // Fetch list of companies on component mount
  useEffect(() => {
    axios.get("http://localhost:8000/companies")
      .then(res => setCompanies(res.data))
      .catch(err => {
        console.error("Error fetching companies", err);
        setErrorMessage("Failed to load companies.");
      });
  }, []);

  // Fetch all required company data when user selects a company
  const fetchCompanyData = async (ticker) => {
    try {
      setErrorMessage(""); // Clear previous errors
      const [
        summary, financials, trend, news, rating, forecast, stock, trendComp
      ] = await Promise.all([
        axios.get(`http://localhost:8000/company-summary/${ticker}`),
        axios.get(`http://localhost:8000/financial-statements/${ticker}`),
        axios.get(`http://localhost:8000/stock-trend/${ticker}`),
        axios.get(`http://localhost:8000/sentiment-news/${ticker}`),
        axios.get(`http://localhost:8000/credit-rating/${ticker}`),
        axios.get(`http://localhost:8000/forecast-plot/${ticker}`),
        axios.get(`http://localhost:8000/stock-plot/${ticker}`),
        axios.get(`http://localhost:8000/trend-components/${ticker}`)
      ]);

      setCompanyData({
        summary: summary.data,
        financials: financials.data,
        trend: trend.data,
        news: news.data
      });

      setCreditRating(rating.data);
      setForecastPlot(forecast.data.image); // Extract `.image` from API response
      setStockPlot(stock.data.image);
      setTrendComponents(trendComp.data.image);
    } catch (error) {
      console.error("Error fetching company data", error);
      setErrorMessage("Failed to fetch company data. Please try again.");
    }
  };

  // Submit Vision & Mission Sentiments
  const handleSubmitVisionMission = async () => {
    try {
      const res = await axios.post(
        "http://localhost:8000/vision-mission-sentiments",
        new URLSearchParams({ vision, mission })
      );
      setVisionMissionSentiment(res.data);
    } catch (error) {
      console.error("Error submitting vision/mission", error);
      setErrorMessage("Failed to submit Vision & Mission.");
    }
  };

  // Perform Investment Analysis
  const analyzeCompany = async () => {
    try {
      const res = await axios.post("http://localhost:8000/investment-analysis");
      setInvestmentAnalysis(res.data);
    } catch (error) {
      console.error("Error analyzing company", error);
      setErrorMessage("Failed to perform investment analysis.");
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Company Investment Analysis</h1>

      {/* Show error message if API fails */}
      {errorMessage && <p className="text-red-500 font-bold">{errorMessage}</p>}

      {/* Company Selection Dropdown */}
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
          <option key={comp.Symbol} value={comp.Symbol}>{comp.Security}</option>
        ))}
      </select>

      {companyData && (
        <div className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold">Summary</h2>
            <p>{companyData.summary?.longBusinessSummary || "No summary available"}</p>
          </div>

          <div>
            <h2 className="text-xl font-semibold">🏢 Company Information</h2>
            <p><strong>Name:</strong> {companyData.summary?.longName || "N/A"}</p>
            <p><strong>Address:</strong> {companyData.summary?.address1}, {companyData.summary?.city}, {companyData.summary?.state}, {companyData.summary?.country}</p>
            <p><strong>Phone:</strong> {companyData.summary?.phone || "N/A"}</p>
            <p>
              <strong>Website:</strong>
              <a href={companyData.summary?.website} target="_blank" rel="noopener noreferrer" className="text-blue-500"> {companyData.summary?.website}</a>
            </p>
            <p><strong>Sector:</strong> {companyData.summary?.sector || "N/A"}</p>
            <p><strong>Industry:</strong> {companyData.summary?.industry || "N/A"}</p>
            <p><strong>Full-Time Employees:</strong> {companyData.summary?.fullTimeEmployees?.toLocaleString() || "N/A"}</p>
          </div>

          {/* Financial Statements Section */}
          <div>
            <h2 className="text-2xl font-semibold mt-6">Financial Statements</h2>

            {/* Income Statement */}
            {companyData.financials?.income_statement && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold mb-2">📊 Income Statement</h3>
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-200">
                      <th className="border p-2 text-left">Metric</th>
                      <th className="border p-2 text-right">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(companyData.financials.income_statement).map(([key, value]) => (
                      <tr key={key}>
                        <td className="border p-2 font-semibold">{key}</td>
                        <td className="border p-2 text-right">{value.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Balance Sheet */}
            {companyData.financials?.balance_sheet && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold mb-2">📋 Balance Sheet</h3>
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-200">
                      <th className="border p-2 text-left">Metric</th>
                      <th className="border p-2 text-right">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(companyData.financials.balance_sheet).map(([key, value]) => (
                      <tr key={key}>
                        <td className="border p-2 font-semibold">{key}</td>
                        <td className="border p-2 text-right">{value.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Cash Flow Statement */}
            {companyData.financials?.cashflow && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold mb-2">💰 Cash Flow Statement</h3>
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-200">
                      <th className="border p-2 text-left">Metric</th>
                      <th className="border p-2 text-right">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(companyData.financials.cashflow).map(([key, value]) => (
                      <tr key={key}>
                        <td className="border p-2 font-semibold">{key}</td>
                        <td className="border p-2 text-right">{value.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Display Stock Trend */}
          <div>
            <h2 className="text-xl font-semibold">Stock Trend</h2>
            <p className="font-semibold">{companyData.trend?.current_trend || "No trend data available"}</p>
          </div>

          {/* Display Plots */}
          {stockPlot && (
            <Plot
              data={stockPlot.data}
              layout={stockPlot.layout}
            />
          )}
          {forecastPlot && <img src={`data:image/png;base64,${forecastPlot}`} alt="Forecast Plot" className="w-full mt-4" />}
          {trendComponents && <img src={`data:image/png;base64,${trendComponents}`} alt="Trend Components" className="w-full mt-4" />}

          {/* Display News Sentiment */}
          <div>
            <h2 className="text-xl font-semibold">News Sentiment</h2>
            <p className="font-semibold">
              Overall Sentiment: {companyData.news?.overall_sentiment || "N/A"}
            </p>

            {/* Show News Headlines */}
            {companyData.news?.headlines?.length > 0 ? (
              <div className="mt-2">
                <h3 className="font-semibold">Top Headlines:</h3>
                <ul className="list-disc ml-5">
                  {companyData.news.headlines.map((headline, index) => (
                    <li key={index} className="text-gray-800">{headline}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-gray-500">No headlines available</p>
            )}
          </div>



          {/* Credit Rating */}
          <div>
            <h2 className="text-xl font-semibold">Credit Rating</h2>
            <p className="font-bold text-red-500">{creditRating?.ratings?.join(", ") || "No credit rating available"}</p>
          </div>
        </div>
      )}

      {/* Vision & Mission Form */}
      <div className="mt-6">
        <h2 className="text-xl font-semibold">Enter Vision & Mission</h2>
        <textarea className="w-full p-2 border mb-2" rows="3" placeholder="Enter Vision" value={vision} onChange={(e) => setVision(e.target.value)} />
        <textarea className="w-full p-2 border mb-2" rows="3" placeholder="Enter Mission" value={mission} onChange={(e) => setMission(e.target.value)} />
        <button className="bg-blue-500 text-white px-4 py-2" onClick={handleSubmitVisionMission}>Submit</button>
      </div>

      {/* Analyze Investment Button */}
      <button className="mt-6 bg-green-500 text-white px-4 py-2" onClick={analyzeCompany}>Analyze Investment</button>

      {/* Display Investment Analysis */}
      {investmentAnalysis && (
        <div className="mt-4">
          <h2 className="text-xl font-semibold">Investment Analysis</h2>
          <p className="font-semibold">{investmentAnalysis.investment_decision || "No decision available"}</p>
        </div>
      )}
    </div>
  );
}
