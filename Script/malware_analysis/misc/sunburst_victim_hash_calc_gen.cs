using Microsoft.Win32;
using System;
using System.IO;
using System.Linq;
using System.Net.NetworkInformation;
using System.Security.Cryptography;
using System.Text;

namespace getorcreateuserid
{
    class Program
    {
		static void Main(string[] args)
        {
			// Verify the data output
			// MacAddr
			var macAddr =
				(
					from nic in NetworkInterface.GetAllNetworkInterfaces()
					where nic.OperationalStatus == OperationalStatus.Up
					select nic.GetPhysicalAddress().ToString()
				).FirstOrDefault();
			Console.WriteLine(macAddr);

			// MachineGuid
			try
			{
				using (RegistryKey registryKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
				{
					using (RegistryKey registryKey2 = registryKey.OpenSubKey(@"SOFTWARE\Microsoft\Cryptography"))
					{
						object value = registryKey2.GetValue("MachineGuid", (object)"default");
						if (value != null)
						{
							// Junk Code
							if (value.GetType() == typeof(byte[]))
							{
								Console.WriteLine("asd");
								//return OrionImprovementBusinessLayer.ByteArrayToHexString((byte[])value);
							}
							// Junk Code
							if (value.GetType() == typeof(string[]))
							{
								string a = string.Join("\n", (string[])value);
								Console.WriteLine(a);
							}
							// Always touch this function at last
							Console.WriteLine(value.ToString());
						}
					}
				}
			}
			catch (Exception ex) {}
			Console.WriteLine();

			// Domain name
			//IPGlobalProperties properties = IPGlobalProperties.GetIPGlobalProperties();
			//Console.WriteLine("Domain name:   {0}", properties.DomainName);
			
			// Working code here to calculate the SunBurst hash
			byte[] hash64;
			string[] guid_components_lines = File.ReadAllLines(@"Your folder path");
			foreach (string guid_components_line in guid_components_lines)
			{
				string[] guid_components = guid_components_line.Split(',');
				Console.WriteLine(guid_components[0]);
				Console.WriteLine(guid_components[1]);
				Console.WriteLine(guid_components[2]);
				Console.WriteLine(guid_components[3]);
				string text = guid_components[1];

				hash64 = new byte[8];
				Array.Clear(hash64, 0, hash64.Length);
				if (text == null)
				{
					Console.WriteLine("FALSE");
				}
				text += guid_components[2];
				try
				{
					text += guid_components[3];
				}
				catch
				{ }
				using (MD5 md = MD5.Create())
				{
					byte[] bytes = Encoding.ASCII.GetBytes(text);
					byte[] array = md.ComputeHash(bytes);
					if (array.Length < hash64.Length)
					{
						Console.WriteLine("FALSE");
					}

					byte[] array2;
					for (int i = 0; i < array.Length; i++)
					{
						array2 = hash64;
						int num = i % hash64.Length;
						array2[num] ^= array[i];
						//Console.Write(array2[num].ToString("X"));
					}
					for (int idx = 0; idx < hash64.Length; idx++) {
						Console.Write(hash64[idx].ToString("X"));
					}
				}
				Console.WriteLine();
			}
			Console.WriteLine("END");
		}
	}
}
