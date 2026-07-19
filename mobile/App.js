import React, { useState } from 'react';
import { StyleSheet, Text, View, Button, Image } from 'react-native';

export default function App() {
  const [result, setResult] = useState(null);

  const mockIdentify = () => {
    setResult("Identified: Monstera Deliciosa. Care: Medium indirect light.");
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>PlantGuide Mobile</Text>
      <View style={styles.placeholder}>
        <Text style={styles.placeholderText}>Camera View Placeholder</Text>
      </View>
      <Button title="Identify Plant" onPress={mockIdentify} />
      {result && <Text style={styles.result}>{result}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  placeholder: {
    width: 300,
    height: 300,
    backgroundColor: '#eee',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  placeholderText: {
    color: '#888',
  },
  result: {
    marginTop: 20,
    fontSize: 16,
    color: 'green',
    textAlign: 'center',
  }
});