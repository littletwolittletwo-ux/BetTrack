import { useState, useEffect } from "react";
import { api, getRole } from "@/auth";
import { Eye, Download, Calendar, DollarSign, TrendingUp, TrendingDown, Trash2 } from "lucide-react";

interface Bet {
  id: number;
  set_id: number;
  bookmaker_id: number;
  stake_manual: number;
  odds_numeric: number;
  potential_return: number;
  cashout_amount: number;
  result_status: string | null;
  profit: number;
  uploaded_at: string;
  event_text: string;
  image_path: string;
  raw_ocr_json: any;
  bet_type: string;
  commission_rate: number;
}

export default function AllUploads() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBet, setSelectedBet] = useState<Bet | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);
  const role = getRole();

  useEffect(() => {
    loadAllBets();
  }, []);

  const loadAllBets = async () => {
    try {
      const response = await api.get("/bets/all?limit=100");
      setBets(response.data);
    } catch (error) {
      console.error("Failed to load bets:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  const getResultIcon = (result: string | null, profit: number) => {
    if (profit > 0) return <TrendingUp className="text-green-400" size={16} />;
    if (profit < 0) return <TrendingDown className="text-red-400" size={16} />;
    return <div className="w-4 h-4 rounded-full bg-gray-500"></div>;
  };

  const getResultColor = (result: string | null, profit: number) => {
    if (profit > 0) return "text-green-400";
    if (profit < 0) return "text-red-400";
    return "text-gray-400";
  };

  const deleteBet = async (betId: number) => {
    if (!confirm(`Are you sure you want to delete bet #${betId}? This action cannot be undone.`)) {
      return;
    }

    setDeleting(betId);
    try {
      await api.delete(`/bets/${betId}`);
      setBets(bets.filter(bet => bet.id !== betId));
    } catch (error) {
      console.error("Failed to delete bet:", error);
      alert("Failed to delete bet. Please try again.");
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-acc"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">All Uploads</h1>
        <p className="text-mut">Comprehensive view of all uploaded betting slips</p>
      </div>

      <div className="grid gap-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card p-4">
            <div className="flex items-center gap-2 text-mut mb-1">
              <Eye size={16} />
              Total Uploads
            </div>
            <div className="text-xl font-bold">{bets.length}</div>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 text-mut mb-1">
              <DollarSign size={16} />
              Total Stakes
            </div>
            <div className="text-xl font-bold">
              ${bets.reduce((sum, bet) => sum + bet.stake_manual, 0).toFixed(2)}
            </div>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 text-mut mb-1">
              <TrendingUp size={16} />
              Total Profit
            </div>
            <div className={`text-xl font-bold ${
              bets.reduce((sum, bet) => sum + bet.profit, 0) >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              ${bets.reduce((sum, bet) => sum + bet.profit, 0).toFixed(2)}
            </div>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 text-mut mb-1">
              <TrendingUp size={16} />
              Win Rate
            </div>
            <div className="text-xl font-bold">
              {bets.filter(b => b.profit > 0).length > 0 ? 
                `${((bets.filter(b => b.profit > 0).length / bets.length) * 100).toFixed(1)}%` : 
                '0%'}
            </div>
          </div>
        </div>

        {/* Bets Table */}
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#0f1721] border-b border-line">
                <tr>
                  <th className="text-left p-4 font-medium">Date</th>
                  <th className="text-left p-4 font-medium">Bet ID</th>
                  <th className="text-left p-4 font-medium">Stakes</th>
                  <th className="text-left p-4 font-medium">Odds</th>
                  <th className="text-left p-4 font-medium">Return</th>
                  <th className="text-left p-4 font-medium">Result</th>
                  <th className="text-left p-4 font-medium">Profit</th>
                  <th className="text-left p-4 font-medium">Event</th>
                  <th className="text-left p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {bets.map((bet) => (
                  <tr key={bet.id} className="border-b border-line/30 hover:bg-[#0f1721]/50">
                    <td className="p-4">
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar size={14} className="text-mut" />
                        {formatDate(bet.uploaded_at)}
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="font-mono text-sm">#{bet.id}</span>
                    </td>
                    <td className="p-4">
                      <span className="font-medium">${bet.stake_manual.toFixed(2)}</span>
                    </td>
                    <td className="p-4">
                      <span className="font-medium">{bet.odds_numeric?.toFixed(2) || 'N/A'}</span>
                    </td>
                    <td className="p-4">
                      <span className="font-medium">
                        {bet.potential_return ? `$${bet.potential_return.toFixed(2)}` : 'N/A'}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {getResultIcon(bet.result_status, bet.profit)}
                        <span className={`text-sm capitalize ${getResultColor(bet.result_status, bet.profit)}`}>
                          {bet.result_status || 'Unknown'}
                        </span>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`font-bold ${getResultColor(bet.result_status, bet.profit)}`}>
                        ${bet.profit.toFixed(2)}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="max-w-xs truncate text-sm text-mut">
                        {bet.event_text?.substring(0, 50) || 'No event text'}...
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => setSelectedBet(bet)}
                          className="btn-sec text-sm px-3 py-1"
                        >
                          <Eye size={14} />
                          View Details
                        </button>
                        {role === "admin" && (
                          <button 
                            onClick={() => deleteBet(bet.id)}
                            disabled={deleting === bet.id}
                            className="btn-sec text-sm px-3 py-1 text-red-400 hover:bg-red-900/20 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Delete bet"
                          >
                            {deleting === bet.id ? (
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-400"></div>
                            ) : (
                              <Trash2 size={14} />
                            )}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {bets.length === 0 && (
          <div className="card p-12 text-center">
            <div className="text-mut mb-4">No betting slips uploaded yet</div>
            <p className="text-sm text-mut">Upload your first betting slip to get started</p>
          </div>
        )}
      </div>

      {/* Bet Details Modal */}
      {selectedBet && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-line rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Bet Details - #{selectedBet.id}</h2>
              <button 
                onClick={() => setSelectedBet(null)}
                className="btn-sec text-sm"
              >
                Close
              </button>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium mb-2">Basic Information</h3>
                  <div className="space-y-2 text-sm">
                    <div><strong>Upload Date:</strong> {formatDate(selectedBet.uploaded_at)}</div>
                    <div><strong>Set ID:</strong> {selectedBet.set_id}</div>
                    <div><strong>Stakes:</strong> ${selectedBet.stake_manual.toFixed(2)}</div>
                    <div><strong>Odds:</strong> {selectedBet.odds_numeric?.toFixed(2) || 'N/A'}</div>
                    <div><strong>Return:</strong> {selectedBet.potential_return ? `$${selectedBet.potential_return.toFixed(2)}` : 'N/A'}</div>
                    <div><strong>Bet Type:</strong> {selectedBet.bet_type || 'N/A'}</div>
                    <div><strong>Commission:</strong> {selectedBet.commission_rate ? `${selectedBet.commission_rate}%` : 'N/A'}</div>
                    <div><strong>Result:</strong> <span className={getResultColor(selectedBet.result_status, selectedBet.profit)}>{selectedBet.result_status || 'Unknown'}</span></div>
                    <div><strong>Profit:</strong> <span className={`font-bold ${getResultColor(selectedBet.result_status, selectedBet.profit)}`}>${selectedBet.profit.toFixed(2)}</span></div>
                  </div>
                </div>

                {selectedBet.raw_ocr_json?.multi_bet_details && (
                  <div>
                    <h3 className="font-medium mb-2">Multi-Bet Breakdown</h3>
                    <div className="space-y-2 text-sm">
                      <div><strong>Total Bets:</strong> {selectedBet.raw_ocr_json.multi_bet_details.total_bets}</div>
                      <div><strong>Total Stakes:</strong> ${selectedBet.raw_ocr_json.multi_bet_details.total_stakes.toFixed(2)}</div>
                      <div><strong>Total Returns:</strong> ${selectedBet.raw_ocr_json.multi_bet_details.total_returns.toFixed(2)}</div>
                      
                      <div className="mt-4">
                        <strong>Individual Bets:</strong>
                        <div className="mt-2 space-y-1">
                          {selectedBet.raw_ocr_json.multi_bet_details.individual_bets.map((bet: any, idx: number) => (
                            <div key={idx} className="bg-[#0f1721] p-2 rounded text-xs">
                              Bet {bet.bet_number}: @{bet.odds} • ${bet.stake} stake • ${bet.actual_return} return • <span className={bet.profit >= 0 ? 'text-green-400' : 'text-red-400'}>${bet.profit} profit</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="font-medium mb-2">Betting Slip Image</h3>
                  <div className="bg-[#0f1721] p-4 rounded">
                    {selectedBet.image_path ? (
                      <img 
                        src={`/files/${selectedBet.image_path}`} 
                        alt="Betting slip"
                        className="max-w-full h-auto rounded"
                        style={{ maxHeight: '400px' }}
                      />
                    ) : (
                      <div className="text-center text-mut py-8">No image available</div>
                    )}
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-medium mb-2">OCR Extracted Text</h3>
                <div className="bg-[#0f1721] p-4 rounded text-xs font-mono max-h-96 overflow-y-auto">
                  {selectedBet.event_text || 'No OCR text available'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}