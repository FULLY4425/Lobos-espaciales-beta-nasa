// KSP 1.12.x / Unity 2019.4. C# 5, built against the user's own KSP assemblies.
using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Threading;
using UnityEngine;
using KSP.UI.Screens;

[KSPAddon(KSPAddon.Startup.Flight, false)]
public sealed class LobosWeather : MonoBehaviour
{
    [Serializable] public class MapWeather { public string schema; public bool enabled; public string scenario; public float windDirection; }
    private bool window, simulationEnabled, forces, followMap;
    private volatile bool busy;
    private Rect rect = new Rect(30, 90, 330, 310);
    private int scenario;
    private float direction = 90, nextPoll, lastMapAt = -100;
    private volatile string pending;
    private bool mapEnabled;
    private string status = "Entrenamiento desactivado";
    private ApplicationLauncherButton button;
    private Texture2D icon;
    private ParticleSystem dust;
    private Material dustMaterial;
    private readonly HashSet<Rigidbody> bodies = new HashSet<Rigidbody>();
    private readonly string[] names = { "Despejado", "Viento y rafagas", "Polvo", "Tormenta" };
    private readonly string[] keys = { "clear", "wind", "dust", "storm" };
    private readonly float[] speeds = { 0, 12, 8, 25 }, gusts = { 0, 20, 14, 40 };

    public void Start() { GameEvents.onGUIApplicationLauncherReady.Add(AddButton); if (ApplicationLauncher.Ready) AddButton(); }
    private void AddButton()
    {
        if (button != null || ApplicationLauncher.Instance == null) return;
        icon = new Texture2D(32, 32); Color[] pixels = new Color[1024];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = (i / 32 > 12 && i / 32 < 20) ? Color.white : new Color(.55f, .3f, .12f);
        icon.SetPixels(pixels); icon.Apply();
        button = ApplicationLauncher.Instance.AddModApplication(delegate { window = true; }, delegate { window = false; }, null, null, null, null, ApplicationLauncher.AppScenes.FLIGHT, icon);
    }
    public void Update()
    {
        if (Input.GetKey(KeyCode.LeftAlt) && Input.GetKeyDown(KeyCode.W)) window = !window;
        if (pending != null)
        {
            string text = pending; pending = null;
            try {
                MapWeather data = JsonUtility.FromJson<MapWeather>(text);
                int index = data == null ? -1 : Array.IndexOf(keys, data.scenario);
                if (data != null && data.schema == "ksp-training-weather-v1" && index >= 0 && !float.IsNaN(data.windDirection) && !float.IsInfinity(data.windDirection) && data.windDirection >= 0 && data.windDirection < 360)
                { if (followMap) { scenario = index; direction = data.windDirection; mapEnabled = data.enabled; lastMapAt = Time.realtimeSinceStartup; } }
            } catch { /* Invalid or foreign response never enables effects. */ }
        }
        if (followMap && !busy && Time.realtimeSinceStartup >= nextPoll)
        { nextPoll = Time.realtimeSinceStartup + 2; busy = true; ThreadPool.QueueUserWorkItem(ReadMap); }
        Vessel vessel = FlightGlobals.ActiveVessel;
        bool active = CanSimulate(vessel);
        if (!active) { if (dust != null) dust.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear); return; }
        UpdateDust(vessel);
    }
    private void ReadMap(object unused)
    {
        try {
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:7173/api/ksp/weather");
            request.Timeout = 1000; request.ReadWriteTimeout = 1000; request.AllowAutoRedirect = false; request.Proxy = null;
            using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
            using (StreamReader reader = new StreamReader(response.GetResponseStream()))
            { char[] chars = new char[4097]; int n = reader.ReadBlock(chars, 0, chars.Length); if (n <= 4096) pending = new string(chars, 0, n); }
        } catch { /* Stale map disables effects after five seconds. No remote URLs. */ }
        finally { busy = false; }
    }
    private bool CanSimulate(Vessel v)
    {
        return simulationEnabled && (!followMap || (mapEnabled && Time.realtimeSinceStartup - lastMapAt < 5)) &&
            HighLogic.LoadedSceneIsFlight && !FlightDriver.Pause && TimeWarp.CurrentRateIndex == 0 &&
            v != null && v.loaded && !v.packed && !v.isEVA && v.mainBody != null && v.mainBody.name == "Duna" &&
            v.mainBody.atmosphere && v.altitude - v.terrainAltitude < 200 && v.srfSpeed < 100;
    }
    private Vector3 Wind(Vessel v)
    {
        Vector3 up = ((Vector3)(v.CoM - v.mainBody.position)).normalized;
        Vector3 north = Vector3.ProjectOnPlane(v.mainBody.transform.up, up).normalized;
        if (north.sqrMagnitude < .01f) north = Vector3.ProjectOnPlane(Vector3.forward, up).normalized;
        Vector3 east = Vector3.Cross(north, up).normalized;
        float angle = direction * Mathf.Deg2Rad;
        float speed = Mathf.Lerp(speeds[scenario], gusts[scenario], .5f + .5f * Mathf.Sin(Time.time * .7f));
        return -(north * Mathf.Cos(angle) + east * Mathf.Sin(angle)) * speed;
    }
    public void FixedUpdate()
    {
        Vessel v = FlightGlobals.ActiveVessel;
        if (!forces || !CanSimulate(v) || scenario == 0) return;
        // Simplified incremental drag relative to KSP's still-air drag; no control/autopilot calls.
        Vector3 velocity = (Vector3)v.srf_velocity, relative = velocity - Wind(v);
        double density = v.atmDensity, massKg = v.GetTotalMass() * 1000;
        if (double.IsNaN(density) || double.IsInfinity(density) || density < 0 || double.IsNaN(massKg) || double.IsInfinity(massKg) || massKg <= 0) return;
        Vector3 delta = -.5f * (float)density * 10f * (relative.magnitude * relative - velocity.magnitude * velocity);
        Vector3 acceleration = Vector3.ClampMagnitude(delta / (float)massKg, .2f);
        if (float.IsNaN(acceleration.sqrMagnitude) || float.IsInfinity(acceleration.sqrMagnitude)) return;
        bodies.Clear();
        foreach (Part part in v.parts) if (part != null && part.rb != null && !part.rb.isKinematic && bodies.Add(part.rb)) part.rb.AddForce(acceleration, ForceMode.Acceleration);
    }
    private void UpdateDust(Vessel v)
    {
        if (scenario < 2) { if (dust != null) dust.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear); return; }
        if (dust == null) {
            GameObject go = new GameObject("LobosTrainingDust"); dust = go.AddComponent<ParticleSystem>(); dust.Stop();
            ParticleSystem.MainModule main = dust.main; main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.maxParticles = 160; main.startLifetime = 2; main.startSize = .25f; main.startSpeed = 0;
            main.startColor = new Color(.7f, .4f, .2f, .22f);
            ParticleSystem.ShapeModule shape = dust.shape; shape.shapeType = ParticleSystemShapeType.Sphere; shape.radius = 12;
            ParticleSystem.EmissionModule emission = dust.emission; emission.rateOverTime = 30;
            Shader shader = Shader.Find("Particles/Alpha Blended");
            if (shader != null) { dustMaterial = new Material(shader); dust.GetComponent<ParticleSystemRenderer>().sharedMaterial = dustMaterial; }
        }
        Vector3 up = ((Vector3)(v.CoM - v.mainBody.position)).normalized;
        dust.transform.position = (Vector3)v.CoM + up * 3;
        Vector3 wind = Wind(v); ParticleSystem.VelocityOverLifetimeModule movement = dust.velocityOverLifetime;
        movement.enabled = true; movement.space = ParticleSystemSimulationSpace.World;
        movement.x = wind.x; movement.y = wind.y; movement.z = wind.z;
        if (!dust.isPlaying) dust.Play();
    }
    public void OnGUI() { if (window) rect = GUILayout.Window(GetInstanceID(), rect, DrawWindow, "Lobos · clima SIMULADO"); }
    private void DrawWindow(int id)
    {
        simulationEnabled = GUILayout.Toggle(simulationEnabled, "Activar entrenamiento (solo Duna / superficie)");
        forces = GUILayout.Toggle(forces, "Aplicar fuerzas al rover (opcional)");
        bool next = GUILayout.Toggle(followMap, "Seguir mapa local en puerto 7173");
        if (next != followMap) { followMap = next; lastMapAt = -100; mapEnabled = false; }
        if (!followMap) { scenario = GUILayout.SelectionGrid(scenario, names, 2); direction = GUILayout.HorizontalSlider(direction, 0, 359); }
        GUILayout.Label(names[scenario] + ": " + speeds[scenario] + " m/s; rafagas " + gusts[scenario] + " m/s; desde " + Mathf.RoundToInt(direction) + " grados");
        status = CanSimulate(FlightGlobals.ActiveVessel) ? (forces ? "Efectos y fuerzas activos" : "Solo efectos visuales") : "En pausa / desactivado / fuera de Duna";
        GUILayout.Label(status); GUILayout.Label("Modelo educativo. No es meteorologia real. Guarda una copia de tu partida para probar.");
        if (GUILayout.Button("Detener efectos")) { simulationEnabled = false; forces = false; }
        GUI.DragWindow(new Rect(0, 0, 330, 25));
    }
    public void OnDestroy()
    {
        simulationEnabled = false; forces = false; GameEvents.onGUIApplicationLauncherReady.Remove(AddButton);
        if (button != null && ApplicationLauncher.Instance != null) ApplicationLauncher.Instance.RemoveModApplication(button);
        if (icon != null) Destroy(icon);
        if (dust != null) { if (dustMaterial != null) Destroy(dustMaterial); Destroy(dust.gameObject); }
    }
}
