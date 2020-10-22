using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Threading;


enum RotationMode
{
    ROTATION_MODE_EULER = 0,
    ROTATION_MODE_QUATERNION = 1,
}
public class NetworkedTracker : MonoBehaviour
{
    private Thread receiveThread;
    private UdpClient client;
    private IPAddress multicastGroupAddress;
    private Vector3 translation = new Vector3();
    private Vector3 eulerRotation = new Vector3();
    private Vector4 quaternion = new Vector4();
    private RotationMode rotationMode;
    [SerializeField] private string multicastGroup;
    [SerializeField] private int port = 8051;
    [SerializeField] private String deviceFilter = "";

    // Start is called before the first frame update
    void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        multicastGroupAddress = (multicastGroup != null && multicastGroup.Length > 0) ? IPAddress.Parse(multicastGroup) : null;
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = translation;
        switch (rotationMode)
        {
            case RotationMode.ROTATION_MODE_EULER:
                transform.eulerAngles = eulerRotation;
                break;
            case RotationMode.ROTATION_MODE_QUATERNION:
                transform.rotation = new Quaternion(quaternion.w, quaternion.x, quaternion.y, quaternion.z);
                break;
        }
    }

    void OnApplicationQuit()
    {
        if (receiveThread != null)
        {
            receiveThread = null;
        }
        client.Close();
    }

    // receive thread
    private void ReceiveData()
    {
        port = 8051;
        client = new UdpClient(port);
        if (multicastGroupAddress != null)
        {
            client.JoinMulticastGroup(multicastGroupAddress);
        }
        print("Starting Server");
        while (receiveThread != null)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);

                String device = System.Text.Encoding.Default.GetString(data, 0, 31);
                if (device.IndexOf(deviceFilter) >= 0)
                {
                    rotationMode = (RotationMode) data[31];
                    translation.x = (float)BitConverter.ToDouble(data, 32 + 0 * 8);
                    translation.y = (float)BitConverter.ToDouble(data, 32 + 1 * 8);
                    translation.z = (float)BitConverter.ToDouble(data, 32 + 2 * 8);

                    switch (rotationMode)
                    {
                        case RotationMode.ROTATION_MODE_EULER:
                            eulerRotation.x = (float)BitConverter.ToDouble(data, 32 + 3 * 8);
                            eulerRotation.y = (float)BitConverter.ToDouble(data, 32 + 4 * 8);
                            eulerRotation.z = (float)BitConverter.ToDouble(data, 32 + 5 * 8);

                            break;
                        case RotationMode.ROTATION_MODE_QUATERNION:
                            quaternion.w = (float)BitConverter.ToDouble(data, 32 + 3 * 8);
                            quaternion.x = (float)BitConverter.ToDouble(data, 32 + 4 * 8);
                            quaternion.y = (float)BitConverter.ToDouble(data, 32 + 5 * 8);
                            quaternion.z = (float)BitConverter.ToDouble(data, 32 + 6 * 8);
                            break;
                    }
                }
            }
            catch (Exception err)
            {
                print(err.ToString());
            }
        }
    }

}
