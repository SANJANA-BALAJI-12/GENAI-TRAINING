import { motion } from 'framer-motion';
import { CheckSquare, Calendar, Package, AlertTriangle, Clock } from 'lucide-react';
import { useState } from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in-progress' | 'completed';
  dueDate: string;
  assignedTo?: string;
  sector?: string;
}

interface InventoryItem {
  id: string;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  threshold: number;
  lastUpdated: string;
}

export default function TaskInventory() {
  const [activeTab, setActiveTab] = useState<'tasks' | 'inventory'>('tasks');

  // Mock tasks data
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Spray Fungicide on Sector Beta',
      description: 'Apply chlorothalonil fungicide to prevent rust development',
      priority: 'high',
      status: 'pending',
      dueDate: '2024-04-12',
      sector: 'Beta',
      assignedTo: 'John'
    },
    {
      id: '2',
      title: 'Irrigate Sector Gamma',
      description: 'Deep irrigation to improve soil moisture levels',
      priority: 'medium',
      status: 'in-progress',
      dueDate: '2024-04-11',
      sector: 'Gamma',
      assignedTo: 'Mike'
    },
    {
      id: '3',
      title: 'Harvest Wheat in Sector Alpha',
      description: 'Begin wheat harvest when moisture levels reach optimal',
      priority: 'high',
      status: 'pending',
      dueDate: '2024-04-15',
      sector: 'Alpha',
      assignedTo: 'Sarah'
    }
  ]);

  // Mock inventory data
  const [inventory] = useState<InventoryItem[]>([
    {
      id: '1',
      name: 'Chlorothalonil Fungicide',
      category: 'Pesticides',
      quantity: 45,
      unit: 'L',
      threshold: 50,
      lastUpdated: '2024-04-10'
    },
    {
      id: '2',
      name: 'Nitrogen Fertilizer',
      category: 'Fertilizers',
      quantity: 120,
      unit: 'kg',
      threshold: 100,
      lastUpdated: '2024-04-09'
    },
    {
      id: '3',
      name: 'Irrigation Pipes',
      category: 'Equipment',
      quantity: 8,
      unit: 'units',
      threshold: 10,
      lastUpdated: '2024-04-08'
    },
    {
      id: '4',
      name: 'Seeds - Wheat',
      category: 'Seeds',
      quantity: 25,
      unit: 'kg',
      threshold: 50,
      lastUpdated: '2024-04-07'
    }
  ]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 border-red-400/50';
      case 'medium': return 'text-yellow-400 border-yellow-400/50';
      case 'low': return 'text-green-400 border-green-400/50';
      default: return 'text-gray-400 border-gray-400/50';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-500/20';
      case 'in-progress': return 'text-blue-400 bg-blue-500/20';
      case 'pending': return 'text-orange-400 bg-orange-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const updateTaskStatus = (taskId: string, newStatus: Task['status']) => {
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, status: newStatus } : task
    ));
  };

  const lowStockItems = inventory.filter(item => item.quantity <= item.threshold);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white drop-shadow-md tracking-wide">Operations Management</h2>

        {/* Tab Navigation */}
        <div className="flex bg-white/10 rounded-lg p-1">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab('tasks')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'tasks'
                ? 'bg-nature-500 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <CheckSquare className="w-4 h-4 inline mr-2" />
            Tasks
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab('inventory')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'inventory'
                ? 'bg-nature-500 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <Package className="w-4 h-4 inline mr-2" />
            Inventory
          </motion.button>
        </div>
      </div>

      {activeTab === 'tasks' ? (
        <div className="space-y-6">
          {/* Task Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Tasks', value: tasks.length, color: 'text-blue-400' },
              { label: 'Pending', value: tasks.filter(t => t.status === 'pending').length, color: 'text-orange-400' },
              { label: 'In Progress', value: tasks.filter(t => t.status === 'in-progress').length, color: 'text-blue-400' },
              { label: 'Completed', value: tasks.filter(t => t.status === 'completed').length, color: 'text-green-400' }
            ].map((stat, idx) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="glass-panel p-4 text-center"
              >
                <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
                <div className="text-white/70 text-sm">{stat.label}</div>
              </motion.div>
            ))}
          </div>

          {/* Tasks List */}
          <div className="space-y-4">
            {tasks.map((task, idx) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="glass-panel p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-bold text-white">{task.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(task.priority)}`}>
                        {task.priority.toUpperCase()}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(task.status)}`}>
                        {task.status.replace('-', ' ').toUpperCase()}
                      </span>
                    </div>
                    <p className="text-white/70 mb-3">{task.description}</p>
                    <div className="flex items-center gap-4 text-sm text-white/60">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                      </div>
                      {task.sector && (
                        <div className="flex items-center gap-1">
                          <Package className="w-4 h-4" />
                          <span>{task.sector}</span>
                        </div>
                      )}
                      {task.assignedTo && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>{task.assignedTo}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    {task.status !== 'completed' && (
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => updateTaskStatus(task.id, task.status === 'pending' ? 'in-progress' : 'completed')}
                        className="px-3 py-1 bg-nature-500 hover:bg-nature-600 text-white text-sm rounded-lg transition-colors"
                      >
                        {task.status === 'pending' ? 'Start' : 'Complete'}
                      </motion.button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Low Stock Alert */}
          {lowStockItems.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-panel p-4 border-l-4 border-orange-400"
            >
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-orange-400" />
                <div>
                  <h3 className="text-white font-bold">Low Stock Alert</h3>
                  <p className="text-white/70 text-sm">
                    {lowStockItems.length} item{lowStockItems.length > 1 ? 's' : ''} below threshold levels
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Inventory Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {inventory.map((item, idx) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.1 }}
                className={`glass-panel p-6 ${item.quantity <= item.threshold ? 'border-l-4 border-orange-400' : ''}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">{item.name}</h3>
                    <p className="text-white/60 text-sm">{item.category}</p>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${item.quantity <= item.threshold ? 'text-orange-400' : 'text-green-400'}`}>
                      {item.quantity} {item.unit}
                    </div>
                    <div className="text-white/60 text-xs">Threshold: {item.threshold} {item.unit}</div>
                  </div>
                </div>

                <div className="w-full bg-white/10 rounded-full h-2 mb-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min((item.quantity / item.threshold) * 100, 100)}%` }}
                    transition={{ duration: 1, delay: idx * 0.1 }}
                    className={`h-full rounded-full ${
                      item.quantity <= item.threshold ? 'bg-orange-500' : 'bg-green-500'
                    }`}
                  />
                </div>

                <div className="flex justify-between text-xs text-white/60">
                  <span>Last updated: {new Date(item.lastUpdated).toLocaleDateString()}</span>
                  <span className={item.quantity <= item.threshold ? 'text-orange-400' : 'text-green-400'}>
                    {item.quantity <= item.threshold ? 'Low Stock' : 'In Stock'}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}