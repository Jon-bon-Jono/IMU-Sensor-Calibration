using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.IO.Ports;

using TMPro;
using UnityEngine;

public class Rotate : MonoBehaviour
{
	 //USE SERIAL PORT
    //SerialPort sp = new SerialPort("COM5",19200);
    //Socket clientSocket = new Socket(AddressFamily.InterNetwork,SocketType.Stream,ProtocolType.Tcp);
    //USE TCP SOCKET
    private TcpClient socketConnection;
    private Thread clientReceiveThread;
    public string processedMessage = "";
    public string tcpMessage = "";
    
    byte[] bytes = null;
    public string[] orientation; 
    [SerializeField] private TMP_Text stateText;
    [SerializeField] private Transform cube;
    private Quaternion rawQt;

    // called before the first frame update
    void Start()
    {
       //SERIAL PORT:
       //sp.Open();
       //sp.DtrEnable = true;
       //sp.ReadTimeout = 1000; //Unity might freeze if too high 
		 //TCP:
       ConnectToTcpServer();
    }

    void Update()
    {
        //if socket receives a new message
        if(!tcpMessage.Equals(processedMessage)){
           processedMessage = tcpMessage;
           //Debug.Log("Update's new message: "+tcpMessage);

           //PARSE MESSAGE
           orientation = tcpMessage.Split(';')[1].Split(',')[0].Trim(' ').Split(' ');
           //Debug.Log("After parsing: ");
           //foreach(var item in orientation){ Debug.Log(item.ToString());}
           float qw = float.Parse(orientation[0]);
	        float qx = -float.Parse(orientation[1]);
	        float qy = float.Parse(orientation[2]);
	        float qz = -float.Parse(orientation[3]);
	        setStateText("w: "+qw+"\n x: "+qx+"\n y: "+qy+"\n z:"+qz);
	        rawQt = new Quaternion(qx, -qz, qy, qw); //z,x,y,w
	        cube.rotation = rawQt;
        }
    }
    
    private void ConnectToTcpServer(){
       try {
          clientReceiveThread = new Thread (new ThreadStart(ListenForData));
          clientReceiveThread.IsBackground = true;
          clientReceiveThread.Start();
       }catch(Exception e){
          Debug.Log("On client connect exception "+e);
       }
    }

    private void ListenForData(){
       try{
          socketConnection = new TcpClient("localhost", 65432);
          Byte[] bytes = new Byte[1024];
          while(true){
              using(NetworkStream stream = socketConnection.GetStream()){
                 int length;
                 while((length = stream.Read(bytes, 0, bytes.Length))!=0){
                    var incommingData = new byte[length];
                    Array.Copy(bytes,0,incommingData,0,length);
                    tcpMessage = "";
                    tcpMessage = Encoding.ASCII.GetString(incommingData);
                    //Debug.Log("server message recieved as: " + tcpMessage);
                 }
              }
          }
       }catch(SocketException socketException){
          Debug.Log("Socket exception: " + socketException);
       }
    }

	 void setStateText(string text)
    {
        if (stateText == null) return;
        stateText.text = text;
    }
}
