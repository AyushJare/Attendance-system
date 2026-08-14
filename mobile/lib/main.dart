import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Attendance Tracking',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          elevation: 0,
          backgroundColor: Color(0xFF1E40AF),
        ),
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  double? latitude;
  double? longitude;
  double? gpsAccuracy;
  String message = '';
  bool isLoading = false;
  int employeeId = 1;
  bool isAdmin = false;
  int selectedTab = 0;

  @override
  void initState() {
    super.initState();
    _getLocation();
  }

  Future<void> _getLocation() async {
    try {
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.best,
      );
      setState(() {
        latitude = position.latitude;
        longitude = position.longitude;
        gpsAccuracy = position.accuracy;
      });
    } catch (e) {
      setState(() {
        message = 'Error getting location: $e';
      });
    }
  }

  Future<void> _checkIn() async {
    if (latitude == null || longitude == null) {
      setState(() {
        message = 'Please get location first';
      });
      return;
    }

    setState(() {
      isLoading = true;
      message = '';
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/attendance/check-in?employee_id=$employeeId'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'latitude': latitude,
          'longitude': longitude,
          'gps_accuracy': gpsAccuracy,
          'device_id': 'flutter-device',
          'mock_location': false,
        }),
      );

      final data = jsonDecode(response.body);
      setState(() {
        message = data['message'] ?? 'Check-in processed';
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        message = 'Error: $e';
        isLoading = false;
      });
    }
  }

  Future<void> _checkOut() async {
    if (latitude == null || longitude == null) {
      setState(() {
        message = 'Please get location first';
      });
      return;
    }

    setState(() {
      isLoading = true;
      message = '';
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/attendance/check-out?employee_id=$employeeId'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'latitude': latitude,
          'longitude': longitude,
          'gps_accuracy': gpsAccuracy,
          'device_id': 'flutter-device',
          'mock_location': false,
        }),
      );

      final data = jsonDecode(response.body);
      setState(() {
        message = data['message'] ?? 'Check-out processed';
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        message = 'Error: $e';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Attendance Tracking',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        centerTitle: true,
        actions: [
          GestureDetector(
            onTap: () {
              setState(() {
                isAdmin = !isAdmin;
                employeeId = isAdmin ? 2 : 1;
                selectedTab = 0;
              });
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Center(
                child: Text(
                  isAdmin ? '👨‍💼 Admin' : '👤 Employee',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Enhanced Tab buttons
          Container(
            padding: const EdgeInsets.all(12),
            color: Colors.grey[50],
            child: Row(
              children: [
                Expanded(
                  child: _buildTabButton(
                    label: '📍 Check-In',
                    isActive: selectedTab == 0,
                    onTap: () => setState(() => selectedTab = 0),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildTabButton(
                    label: '📋 History',
                    isActive: selectedTab == 1,
                    onTap: () => setState(() => selectedTab = 1),
                  ),
                ),
                if (isAdmin) ...[
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildTabButton(
                      label: '⚙️ Admin',
                      isActive: selectedTab == 2,
                      onTap: () => setState(() => selectedTab = 2),
                    ),
                  ),
                ],
              ],
            ),
          ),
          
          // Content
          Expanded(
            child: selectedTab == 0
                ? _buildCheckInScreen()
                : selectedTab == 1
                    ? _buildHistoryScreen()
                    : _buildAdminScreen(),
          ),
        ],
      ),
    );
  }

  Widget _buildTabButton({
    required String label,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFF1E40AF) : Colors.white,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isActive ? const Color(0xFF1E40AF) : Colors.grey[300]!,
          ),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: isActive ? Colors.white : Colors.grey[700],
            fontWeight: FontWeight.w600,
            fontSize: 13,
          ),
        ),
      ),
    );
  }

  Widget _buildCheckInScreen() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Location Card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                gradient: LinearGradient(
                  colors: [Colors.blue[50]!, Colors.blue[100]!],
                ),
              ),
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '📍 Current Location',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1E40AF),
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildLocationRow('Latitude', latitude?.toStringAsFixed(6) ?? '---'),
                  const SizedBox(height: 8),
                  _buildLocationRow('Longitude', longitude?.toStringAsFixed(6) ?? '---'),
                  const SizedBox(height: 8),
                  _buildLocationRow('GPS Accuracy', '${gpsAccuracy?.toStringAsFixed(1) ?? "---"}m'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Get Location Button
          ElevatedButton.icon(
            onPressed: _getLocation,
            icon: const Icon(Icons.refresh),
            label: const Text('Refresh Location'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[600],
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 12),

          // Check-In Button
          ElevatedButton(
            onPressed: isLoading ? null : _checkIn,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF10B981),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(color: Colors.white),
                  )
                : const Text(
                    '✓ Check In',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
          ),
          const SizedBox(height: 12),

          // Check-Out Button
          ElevatedButton(
            onPressed: isLoading ? null : _checkOut,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF59E0B),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text(
              '✗ Check Out',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 20),

          // Message
          if (message.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: message.contains('Error')
                    ? Colors.red[50]
                    : Colors.green[50],
                border: Border.all(
                  color: message.contains('Error')
                      ? Colors.red[300]!
                      : Colors.green[300]!,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                message,
                style: TextStyle(
                  color: message.contains('Error')
                      ? Colors.red[700]
                      : Colors.green[700],
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildLocationRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(color: Colors.grey[700], fontWeight: FontWeight.w500),
        ),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Color(0xFF1E40AF),
            fontSize: 15,
          ),
        ),
      ],
    );
  }

  Widget _buildHistoryScreen() {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _fetchHistory(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }

        final records = snapshot.data ?? [];

        if (records.isEmpty) {
          return const Center(
            child: Text('No attendance records yet', style: TextStyle(fontSize: 16)),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: records.length,
          itemBuilder: (context, index) {
            final record = records[index];
            final isValid = record['status'] == '✓ valid';
            return Card(
              elevation: 1,
              margin: const EdgeInsets.only(bottom: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10),
                  border: Border(
                    left: BorderSide(
                      color: isValid ? Colors.green : Colors.orange,
                      width: 4,
                    ),
                  ),
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.all(16),
                  title: Text(
                    record['date'] ?? 'Unknown',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  subtitle: Text(
                    '${record['check_in'] ?? '--:--'} - ${record['check_out'] ?? 'Pending'}',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  trailing: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: isValid ? Colors.green[50] : Colors.orange[50],
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: isValid ? Colors.green[300]! : Colors.orange[300]!,
                      ),
                    ),
                    child: Text(
                      record['status'] ?? 'Unknown',
                      style: TextStyle(
                        color: isValid ? Colors.green[700] : Colors.orange[700],
                        fontWeight: FontWeight.w600,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildAdminScreen() {
    if (!isAdmin) {
      return const Center(child: Text('Admin access only'));
    }

    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _fetchFlaggedCheckIns(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }

        final flags = snapshot.data ?? [];

        if (flags.isEmpty) {
          return const Center(
            child: Text('No flagged check-ins', style: TextStyle(fontSize: 16)),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: flags.length,
          itemBuilder: (context, index) {
            final flag = flags[index];
            final isHigh = flag['severity'] == 'high';
            return Card(
              elevation: 2,
              margin: const EdgeInsets.only(bottom: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  border: Border(
                    top: BorderSide(
                      color: isHigh ? Colors.red : Colors.orange,
                      width: 3,
                    ),
                  ),
                ),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Record #${flag['id']}',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: Color(0xFF1E40AF),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: isHigh ? Colors.red[50] : Colors.orange[50],
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            flag['severity'] ?? 'Unknown',
                            style: TextStyle(
                              color: isHigh ? Colors.red[700] : Colors.orange[700],
                              fontWeight: FontWeight.w600,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey[50],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'Reason: ${flag['reason']}',
                        style: const TextStyle(
                          color: Color(0xFF374151),
                          fontSize: 14,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton(
                            onPressed: () => _approveCheckIn(flag['id']),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF10B981),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: const Text('✓ Approve'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton(
                            onPressed: () => _rejectCheckIn(flag['id']),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFEF4444),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: const Text('✗ Reject'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Future<List<Map<String, dynamic>>> _fetchHistory() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/v1/attendance/history/$employeeId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['records'] ?? []);
      }
      return [];
    } catch (e) {
      throw Exception('Failed to fetch history: $e');
    }
  }

  Future<List<Map<String, dynamic>>> _fetchFlaggedCheckIns() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/v1/admin/suspicious-checkins?employee_id=$employeeId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['records'] ?? []);
      }
      return [];
    } catch (e) {
      throw Exception('Failed to fetch flagged check-ins: $e');
    }
  }

  Future<void> _approveCheckIn(int id) async {
    try {
      await http.post(
        Uri.parse('http://localhost:8000/api/v1/admin/approve/$id?employee_id=$employeeId'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'notes': 'Approved via mobile app'}),
      );
      setState(() {});
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  Future<void> _rejectCheckIn(int id) async {
    try {
      await http.post(
        Uri.parse('http://localhost:8000/api/v1/admin/reject/$id?employee_id=$employeeId'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'notes': 'Rejected via mobile app'}),
      );
      setState(() {});
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }
}